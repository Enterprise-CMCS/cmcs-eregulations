// lib/stacks/fr-stack.ts

import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environment-config';

interface FrStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  vpc: ec2.IVpc;
}

export class FrStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: FrStackProps) {
    super(scope, id, props);

    const { config, vpc } = props;

    // Create SQS Queue
    const queue = new sqs.Queue(this, 'FrQueue', {
      queueName: `${config.stackPrefix}-fr-queue`,
      visibilityTimeout: cdk.Duration.seconds(300),
      retentionPeriod: cdk.Duration.days(5),
    });

    // Create IAM Role for Lambda
    const lambdaRole = new iam.Role(this, 'FrLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
    });

    // Add policies to the role for accessing SQS and logging
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['sqs:ReceiveMessage', 'sqs:DeleteMessage', 'sqs:GetQueueAttributes'],
      resources: [queue.queueArn],
    }));

    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
      resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
    }));

    // // Docker Image Asset for Lambda
    // const dockerImageAsset = new ecr_assets.DockerImageAsset(this, 'FrDockerImage', {
    //   directory: '../solution/fr', // Adjust this path to where the Dockerfile is located
    // });

    // Create Lambda Function using Docker Image
    const frLambda = new lambda.DockerImageFunction(this, 'FrFunction', {
        functionName: `${config.stackPrefix}-fr-function`,
        code: lambda.DockerImageCode.fromImageAsset('../../../solution/parser/fr-parser'), // Specify the path where Dockerfile is located
        timeout: cdk.Duration.seconds(300),
        memorySize: 1024,
        vpc,
        role: lambdaRole,
        environment: {
          STAGE: config.stackPrefix,
        },
      });

    // Outputs
    new cdk.CfnOutput(this, 'FrQueueUrl', {
      value: queue.queueUrl,
      exportName: `${config.stackPrefix}-FrQueueUrl`,
    });

    new cdk.CfnOutput(this, 'FrFunctionArn', {
      value: frLambda.functionArn,
      exportName: `${config.stackPrefix}-FrFunctionArn`,
    });
  }
}
