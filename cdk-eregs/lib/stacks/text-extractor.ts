import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as iam from 'aws-cdk-lib/aws-iam';

export class TextExtractorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const stage = this.node.tryGetContext('stage') || 'dev';

    // ---------------------------
    // SQS Queues
    // ---------------------------

    // Dead Letter Queue
    const deadLetterQueue = new sqs.Queue(this, 'DeadLetterQueue', {
      queueName: `${stage}-text-extractor-dl-queue`,
    });

    // Main Queue
    const textExtractorQueue = new sqs.Queue(this, 'TextExtractorQueue', {
      queueName: `${stage}-text-extractor-queue`,
      visibilityTimeout: cdk.Duration.seconds(900),
      retentionPeriod: cdk.Duration.days(4),
      deadLetterQueue: {
        queue: deadLetterQueue,
        maxReceiveCount: 5,
      },
    });

    // ---------------------------
    // Lambda Function
    // ---------------------------

    // Lambda Function Role (IAM is defined below)
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });

    // Dockerized Lambda Function
    const lambdaFunction = new lambda.DockerImageFunction(this, 'TextExtractorFunction', {
      code: lambda.DockerImageCode.fromImageAsset('../.', {
        file: 'text-extractor/Dockerfile',
      }),
      timeout: cdk.Duration.seconds(900),
      reservedConcurrentExecutions: 10,
      environment: {
        LOG_LEVEL: `ssm:/eregulations/text_extractor/log_level`,
        HTTP_AUTH_USER: `ssm:/eregulations/http/user`,
        HTTP_AUTH_PASSWORD: `ssm:/eregulations/http/password`,
      },
      role: lambdaRole, // Attach IAM role to Lambda
    });

    // SQS Trigger for Lambda
    lambdaFunction.addEventSource(
      new lambda.SqsEventSource(textExtractorQueue, {
        batchSize: 1,
      })
    );

    // ---------------------------
    // IAM Policies and Permissions
    // ---------------------------

    // Attach Managed Policy for VPC Access
    lambdaRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole')
    );

    // SQS Permissions
    textExtractorQueue.grantConsumeMessages(lambdaRole);

    // Textract Permissions
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['textract:DetectDocumentText'],
        resources: ['*'], // Update this to restrict specific resources if possible
      })
    );

    // Secure S3 Bucket Access
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['s3:PutObject', 's3:GetObject', 's3:DeleteObject'],
        resources: [
          `arn:aws:s3:::file-repo-eregs-${stage}/*`,
        ],
        conditions: { Bool: { 'aws:SecureTransport': false } },
        effect: iam.Effect.DENY,
      })
    );

    // Logging Permissions
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*`],
      })
    );

    // ---------------------------
    // Outputs
    // ---------------------------

    new cdk.CfnOutput(this, 'TextExtractorQueueUrl', {
      value: textExtractorQueue.queueUrl,
      description: 'The URL of the Text Extractor SQS queue',
    });

    new cdk.CfnOutput(this, 'TextExtractorQueueArn', {
      value: textExtractorQueue.queueArn,
      description: 'The ARN of the Text Extractor SQS queue',
    });
  }
}
