// lib/stacks/text-extractor-stack.ts
import * as cdk from 'aws-cdk-lib';
import {
  aws_iam as iam,
  aws_logs as logs,
  aws_lambda as lambda,
  aws_sqs as sqs,
  aws_ec2 as ec2,
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
  /** Optional limit on concurrent executions */
  reservedConcurrentExecutions?: number;
}

/**
 * Configuration interface for environment-specific settings.
 * Contains all the external configuration values needed for the stack.
 */
interface EnvironmentConfig {
  /** VPC ID where the Lambda function will be deployed */
  vpcId: string;
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
 * - Docker-based Lambda function for text extraction
 * - SQS Queue with Dead Letter Queue for reliable message processing
 * - IAM roles and policies for secure access
 * - CloudWatch Log Groups for monitoring
 * - VPC Security Group for network isolation
 * - Event Source Mapping for queue integration
 * 
 * The stack is designed to be environment-aware and supports deployment across
 * different stages (dev, staging, prod) through the StageConfig parameter.
 * 
 * @example
 * ```typescript
 * // Create the stack with environment configuration
 * new TextExtractorStack(app, 'text-extractor', {
 *   env: { account: '123456789', region: 'us-east-1' },
 *   lambdaConfig: {
 *     memorySize: 1024,
 *     timeout: 900,
 *     reservedConcurrentExecutions: 10,
 *   },
 *   environmentConfig: {
 *     vpcId: 'vpc-123456',
 *     logLevel: 'DEBUG',
 *     httpUser: 'user',
 *     httpPassword: 'pass'
 *   }
 * }, stageConfig);
 * ```
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

  /**
   * Creates a new instance of TextExtractorStack.
   * 
   * @param scope - The scope in which to define this construct
   * @param id - The scoped construct ID
   * @param props - Configuration properties for the stack
   * @param stageConfig - Environment stage configuration
   */
  constructor(
    scope: Construct, 
    id: string, 
    props: TextExtractorStackProps,
    stageConfig: StageConfig
  ) {
    super(scope, id, props);
    this.stageConfig = stageConfig;

    // Create VPC reference
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', { 
      vpcId: props.environmentConfig.vpcId 
    });

    // Create security group
    const securityGroup = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions',
      allowAllOutbound: true,
    });

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
    const { lambdaRole, logGroup } = this.createLambdaInfrastructure();

    // Create Lambda function
    this.lambda = this.createTextExtractorLambdaFunction(
      props.lambdaConfig,
      props.environmentConfig,
      lambdaRole,
      vpc,
      securityGroup
    );

    // Create event source mapping
    this.createEventSourceMapping();

    // Create stack outputs
    this.createStackOutputs();
  }

  /**
   * Creates and configures the Lambda function with Docker image.
   * 
   * @param config - Lambda function configuration
   * @param envConfig - Environment-specific configuration
   * @param role - IAM role for the function
   * @param vpc - VPC where the function will be deployed
   * @param securityGroup - Security group for the function
   * @returns Configured Lambda function
   * @private
   */
  private createTextExtractorLambdaFunction(
    config: LambdaConfig,
    envConfig: EnvironmentConfig,
    role: iam.Role,
    vpc: ec2.IVpc,
    securityGroup: ec2.SecurityGroup,
  ): lambda.Function {
    const dockerContextPath = path.resolve(__dirname, '../../../solution/text-extractor/');
    console.log('Docker context path:', dockerContextPath);

    return new lambda.DockerImageFunction(this, 'TextExtractorFunction', {
      functionName: this.stageConfig.getResourceName('text-extractor'),
      code: lambda.DockerImageCode.fromImageAsset(dockerContextPath, {
        file: 'Dockerfile',
      }),
      vpc,
      securityGroups: [securityGroup],
      memorySize: config.memorySize,
      timeout: cdk.Duration.seconds(config.timeout),
      reservedConcurrentExecutions: config.reservedConcurrentExecutions,
      environment: {
        LOG_LEVEL: envConfig.logLevel,
        HTTP_AUTH_USER: envConfig.httpUser,
        HTTP_AUTH_PASSWORD: envConfig.httpPassword,
      },
      role,
    });
  }

  /**
   * Creates event source mapping between SQS queue and Lambda function.
   * Configures single-message processing with batch size of 1.
   * 
   * @private
   */
  private createEventSourceMapping() {
    new lambda.EventSourceMapping(this, 'TextExtractorEventSourceMapping', {
      target: this.lambda,
      batchSize: 1,
      eventSourceArn: this.queue.queueArn,
      enabled: true,
    });
  }

  /**
   * Creates Lambda infrastructure including IAM role and log group.
   * Sets up:
   * - CloudWatch Log Group with infinite retention
   * - IAM Role with proper permissions
   * - Required IAM policies for Queue, Textract, and S3 access
   * 
   * @returns Object containing IAM role and Log Group
   * @private
   */
  private createLambdaInfrastructure() {
    const logGroup = new logs.LogGroup(this, 'TextExtractorLogGroup', {
      logGroupName: this.stageConfig.aws.lambda('text-extractor'),
      retention: logs.RetentionDays.INFINITE,
    });

    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      path: this.stageConfig.iamPath,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        this.stageConfig.permissionsBoundaryArn
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      inlinePolicies: {
        QueuePolicy: this.createQueuePolicy(),
        TextDetectionPolicy: this.createTextDetectionPolicy(),
        LambdaPolicy: this.createLambdaPolicy(),
      },
    });

    return { lambdaRole, logGroup };
  }

  /**
   * Creates SQS queue access policy.
   * Grants permissions for message reception and deletion.
   * 
   * @returns IAM policy document for queue access
   * @private
   */
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

  /**
   * Creates Amazon Textract service access policy.
   * Grants permission to use the DetectDocumentText API.
   * 
   * @returns IAM policy document for Textract access
   * @private
   */
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

  /**
   * Creates Lambda execution policy for logs and S3 access.
   * Grants permissions for:
   * - CloudWatch Logs creation and management
   * - S3 object operations on the environment-specific bucket
   * 
   * @returns IAM policy document for Lambda execution
   * @private
   */
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

  /**
   * Creates CloudFormation outputs for stack resources.
   * Exports:
   * - Lambda function ARN
   * - SQS queue URL and ARN
   * These outputs can be imported by other stacks or used for external reference.
   * 
   * @private
   */
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

