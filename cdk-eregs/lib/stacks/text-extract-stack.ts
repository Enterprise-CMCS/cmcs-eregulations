import * as cdk from 'aws-cdk-lib';
import {
  aws_iam as iam,
  aws_logs as logs,
  aws_lambda as lambda,
  aws_sqs as sqs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import * as path from 'path';

/**
 * Configuration interface for Lambda function settings.
 * Defines required and optional parameters for Lambda function configuration.
 */
interface LambdaConfig {
  /** Memory allocation in MB for the Lambda function */
  memorySize: number;
  /** Function timeout in seconds */
  timeout: number;
}

/**
 * Configuration interface for environment-specific settings.
 * Contains all the external configuration values needed for the stack.
 */
interface EnvironmentConfig {
  /** Log level for the Lambda function (e.g., DEBUG, INFO) */
  logLevel: string;
  /** HTTP basic auth username for API authentication */
  httpUser: string;
  /** HTTP basic auth password for API authentication */
  httpPassword: string;
}

/**
 * Properties interface for TextExtractorStack.
 * Extends standard CDK stack properties with custom configuration settings.
 */
export interface TextExtractorStackProps extends cdk.StackProps {
  /** Lambda function configuration settings */
  lambdaConfig: LambdaConfig;
  /** Environment-specific configuration settings */
  environmentConfig: EnvironmentConfig;
}

/**
 * CDK Stack implementation for Text Extractor service.
 *
 * This stack creates a serverless text extraction service with the following components:
 * - Docker-based Lambda function for text extraction using AWS managed VPC
 * - SQS Queue with Dead Letter Queue for reliable message processing
 * - IAM roles and policies for secure access
 * - CloudWatch Log Groups for monitoring
 * - Event Source Mapping for queue integration
 */
export class TextExtractorStack extends cdk.Stack {
  /** The Lambda function that processes text extraction requests */
  public readonly lambda: lambda.Function;
  /** The SQS queue that holds text extraction requests */
  public readonly queue: sqs.Queue;
  /** The Dead Letter Queue for failed message processing */
  private readonly deadLetterQueue: sqs.Queue;
  /** Stage configuration for environment-aware deployments */
  private readonly stageConfig: StageConfig;

  constructor(
    scope: Construct,
    id: string,
    props: TextExtractorStackProps,
    stageConfig: StageConfig
  ) {
    super(scope, id, props);
    this.stageConfig = stageConfig;

    // Create DLQ
    this.deadLetterQueue = new sqs.Queue(this, 'DeadLetterQueue', {
      queueName: this.stageConfig.getResourceName('text-extractor-dl-queue'),
    });

    // Create main queue
    this.queue = new sqs.Queue(this, 'TextExtractorQueue', {
      queueName: this.stageConfig.getResourceName('text-extractor-queue'),
      visibilityTimeout: cdk.Duration.seconds(900),
      retentionPeriod: cdk.Duration.days(4),
      deadLetterQueue: {
        maxReceiveCount: 5,
        queue: this.deadLetterQueue,
      },
    });

    // Create Lambda infrastructure
    const { lambdaRole } = this.createLambdaInfrastructure();

    // Create Lambda function
    this.lambda = this.createTextExtractorLambdaFunction(
      props.lambdaConfig,
      props.environmentConfig,
      lambdaRole
    );

    // Create event source mapping
    this.createEventSourceMapping();

    // Create stack outputs
    this.createStackOutputs();
  }

  private createTextExtractorLambdaFunction(
    config: LambdaConfig,
    envConfig: EnvironmentConfig,
    role: iam.Role,
  ): lambda.Function {
    const dockerContextPath = path.resolve(__dirname, '../../../solution/');

    return new lambda.DockerImageFunction(this, 'TextExtractorFunction', {
      functionName: this.stageConfig.getResourceName('text-extractor'),
      code: lambda.DockerImageCode.fromImageAsset(dockerContextPath, {
        file: 'text-extractor/Dockerfile',
      }),
      memorySize: config.memorySize,
      timeout: cdk.Duration.seconds(config.timeout),
      environment: {
        LOG_LEVEL: envConfig.logLevel,
        HTTP_AUTH_USER: envConfig.httpUser,
        HTTP_AUTH_PASSWORD: envConfig.httpPassword,
      },
      role,
    });
  }

  private createEventSourceMapping() {
    new lambda.EventSourceMapping(this, 'TextExtractorEventSourceMapping', {
      target: this.lambda,
      batchSize: 1,
      eventSourceArn: this.queue.queueArn,
      enabled: true,
    });
  }

  private createLambdaInfrastructure() {
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      path: this.stageConfig.iamPath,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        this.stageConfig.permissionsBoundaryArn
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        QueuePolicy: this.createQueuePolicy(),
        TextDetectionPolicy: this.createTextDetectionPolicy(),
        LambdaPolicy: this.createLambdaPolicy(),
      },
    });

    return { lambdaRole };
  }

  private createQueuePolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'sqs:ReceiveMessage',
            'sqs:DeleteMessage',
            'sqs:GetQueueAttributes'
          ],
          resources: [this.queue.queueArn],
        }),
      ],
    });
  }

  private createTextDetectionPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          sid: 'DetectDocumentText',
          effect: iam.Effect.ALLOW,
          actions: ['textract:DetectDocumentText'],
          resources: ['*'],
        }),
      ],
    });
  }

  private createLambdaPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'logs:CreateLogGroup',
            'logs:CreateLogStream',
            'logs:PutLogEvents'
          ],
          resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            's3:PutObject',
            's3:GetObject',
            's3:DeleteObject'
          ],
          resources: [
            `arn:aws:s3:::file-repo-eregs-${this.stageConfig.environment}*`
          ],
        }),
      ],
    });
  }

  private createStackOutputs() {
    const outputs: Record<string, cdk.CfnOutputProps> = {
      TextExtractorLambdaFunctionQualifiedArn: {
        value: this.lambda.functionArn,
        description: 'Current Lambda function version',
        exportName: this.stageConfig.getResourceName('text-extractor-lambda-arn'),
      },
      TextExtractorQueueUrl: {
        value: this.queue.queueUrl,
        exportName: this.stageConfig.getResourceName('text-extractor-queue-url'),
      },
      TextExtractorQueueArn: {
        value: this.queue.queueArn,
        exportName: this.stageConfig.getResourceName('text-extractor-queue-arn'),
      }
    };

    Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
  }
}

