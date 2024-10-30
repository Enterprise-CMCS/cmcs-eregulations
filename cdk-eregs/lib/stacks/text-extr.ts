// lib/stacks/text-extractor-stack.ts

import * as cdk from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { LambdaFunctionConstruct, DockerLambdaFunctionConstructProps } from '../constructs/lambda-function-construct';
import { EnvironmentConfig } from '../config/environment-config';

interface TextExtractorStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  vpc: ec2.IVpc;
}

export class TextExtractorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: TextExtractorStackProps) {
    super(scope, id, props);

    const { config, vpc } = props;

    // Create SQS Queue
    const queue = new sqs.Queue(this, 'TextExtractorQueue', {
      queueName: `${config.stackPrefix}-text-extractor-queue`,
      visibilityTimeout: cdk.Duration.seconds(900),
      retentionPeriod: cdk.Duration.days(4),
    });

    // Create IAM Role for Lambda
    const lambdaRole = new iam.Role(this, 'TextExtractorLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/path'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy${ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/permissions_boundary_policy')}`
      ),
    });

    // Add policies to the role
    this.addPoliciesToRole(lambdaRole, queue, config);

    // Create Lambda Function
    const lambdaProps: DockerLambdaFunctionConstructProps = {
      functionName: 'text-extractor',
      stage: config.stackPrefix,
      vpc,
      codeType: 'docker',
      dockerImagePath: '../text-extractor',
      timeout: cdk.Duration.seconds(900),
      memorySize: 1024,  // Adjust as needed
      reservedConcurrentExecutions: 10,
      environment: {
        STAGE: config.stackPrefix,
        LOG_LEVEL: ssm.StringParameter.valueForStringParameter(this, '/eregulations/text_extractor/log_level'),
        HTTP_AUTH_USER: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
        HTTP_AUTH_PASSWORD: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
      },
      role: lambdaRole,
    };

    const lambdaFunction = new LambdaFunctionConstruct(this, 'TextExtractorLambda', lambdaProps);

    // Add SQS as event source for Lambda
    lambdaFunction.function.addEventSource(new SqsEventSource(queue, {
      batchSize: 1,
    }));

    // Outputs
    new cdk.CfnOutput(this, 'TextExtractorQueueUrl', {
      value: queue.queueUrl,
      exportName: `${config.stackPrefix}-TextExtractorQueueUrl`,
    });

    new cdk.CfnOutput(this, 'TextExtractorQueueArn', {
      value: queue.queueArn,
      exportName: `${config.stackPrefix}-TextExtractorQueueArn`,
    });
  }

  private addPoliciesToRole(role: iam.Role, queue: sqs.Queue, config: EnvironmentConfig) {
    // QueuePolicy
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['sqs:ReceiveMessage', 'sqs:DeleteMessage', 'sqs:GetQueueAttributes'],
      resources: [queue.queueArn],
    }));

    // TextDetectionPolicy
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['textract:DetectDocumentText'],
      resources: ['*'],
    }));

    // StorageBucketPolicy
    const bucketArn = `arn:aws:s3:::file-repo-eregs-${config.stackPrefix}`;
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.DENY,
      actions: ['*'],
      resources: [
        `arn:aws:s3:::${this.artifactsBucketName}`,
        `${bucketArn}/*`,
      ],
      conditions: {
        Bool: {
          'aws:SecureTransport': false,
        },
      },
    }));

    // S3 access policy
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['s3:PutObject', 's3:GetObject', 's3:DeleteObject'],
      resources: [
        `arn:aws:s3:::${this.artifactsBucketName}`,
        `${bucketArn}*`,
      ],
    }));
  }
}