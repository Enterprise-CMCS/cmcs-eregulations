import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as path from 'path';
import { Construct } from 'constructs';
import { LambdaFunctionConstruct } from '../constructs/lambda-function-construct';

// Define the properties for the LambdaStack
export interface LambdaStackProps extends cdk.StackProps {
  stage: string;
  vpc: ec2.IVpc;  // The VPC where the Lambda will be deployed
  lambdaName: string;
  lambdaMemorySize?: number;
  lambdaTimeout?: number;
  lambdaConcurrency?: number;
  queueVisibilityTimeout?: number;
  queueRetentionPeriod?: number;
  allowedEgressPorts?: number[];
}

export class LambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: LambdaStackProps) {
    super(scope, id, props);

    // Create the SQS queue
    const queue = this.createSqsQueue(props);

    // Create the IAM role for the Lambda function
    const lambdaRole = this.createLambdaRole(queue);

    // Create the security group for the Lambda function
    const securityGroup = this.createSecurityGroup(props.vpc, props.allowedEgressPorts);

    // Create the Docker-based Lambda function
    const dockerLambda = this.createDockerLambda(props, props.vpc, lambdaRole, securityGroup);

    // Add the SQS queue as an event source for the Lambda function
    this.addSqsEventSource(dockerLambda, queue);

    // Create CloudFormation outputs
    this.createOutputs(dockerLambda, queue);
  }

  // Create an SQS queue
  private createSqsQueue(props: LambdaStackProps): sqs.Queue {
    return new sqs.Queue(this, 'TextExtractorQueue', {
      queueName: `${props.stage}-${props.lambdaName}-queue`,
      visibilityTimeout: cdk.Duration.seconds(props.queueVisibilityTimeout || 900),
      retentionPeriod: cdk.Duration.days(props.queueRetentionPeriod || 4),
    });
  }

  // Create the IAM role for the Lambda function
  private createLambdaRole(queue: sqs.Queue): iam.Role {
    const role = new iam.Role(this, 'LambdaFunctionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: this.getParameter('/account_vars/iam/path'),
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy${this.getParameter('/account_vars/iam/permissions_boundary_policy')}`
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole')
      ],
    });

    this.addRolePolicies(role, queue);
    return role;
  }

  // Add necessary policies to the IAM role
  private addRolePolicies(role: iam.Role, queue: sqs.Queue): void {
    // Allow SQS actions
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['sqs:ReceiveMessage', 'sqs:DeleteMessage', 'sqs:GetQueueAttributes'],
      resources: [queue.queueArn],
    }));

    // Allow Textract actions
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['textract:DetectDocumentText'],
      resources: ['*'],
    }));

    // Deny insecure transport
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.DENY,
      actions: ['*'],
      resources: [
        `arn:aws:s3:::${this.stackName}-${this.region}-${this.account}/*`,
        `arn:aws:s3:::file-repo-eregs-${this.node.tryGetContext('stage')}/*`
      ],
      conditions: {
        Bool: { 'aws:SecureTransport': false },
      },
    }));

    // Allow CloudWatch Logs actions
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
      ],
      resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
    }));

    // Allow S3 actions
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:PutObject', 's3:GetObject', 's3:DeleteObject'],
      resources: [
        `arn:aws:s3:::${this.stackName}-${this.region}-${this.account}/*`,
        `arn:aws:s3:::file-repo-eregs-${this.node.tryGetContext('stage')}*`,
      ],
    }));
  }

  // Create a security group for the Lambda function
  private createSecurityGroup(vpc: ec2.IVpc, allowedPorts?: number[]): ec2.SecurityGroup {
    const sg = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions',
      allowAllOutbound: false,
    });

    if (allowedPorts && allowedPorts.length > 0) {
      allowedPorts.forEach(port => {
        sg.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(port), `Allow outbound traffic on port ${port}`);
      });
    } else {
      sg.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.allTcp(), 'Allow all outbound TCP traffic');
    }

    return sg;
  }

  // Create the Docker-based Lambda function
  private createDockerLambda(props: LambdaStackProps, vpc: ec2.IVpc, role: iam.Role, securityGroup: ec2.SecurityGroup): LambdaFunctionConstruct {
    return new LambdaFunctionConstruct(this, 'TextExtractorLambda', {
      functionName: props.lambdaName,
      stage: props.stage,
      vpc,
      codeType: 'docker',
      dockerImagePath: path.join(__dirname, '../../../solution/text-extractor/'),
      environment: {
        STAGE: props.stage,
        LOG_LEVEL: this.getParameter('/eregulations/text_extractor/log_level'),
        HTTP_AUTH_USER: this.getParameter('/eregulations/http/user'),
        HTTP_AUTH_PASSWORD: this.getParameter('/eregulations/http/password'),
      },
      memorySize: props.lambdaMemorySize || 128,
      timeout: cdk.Duration.seconds(props.lambdaTimeout || 900),
      reservedConcurrentExecutions: props.lambdaConcurrency || 10,
      role,
      securityGroups: [securityGroup],
    });
  }

  // Add the SQS queue as an event source for the Lambda function
  private addSqsEventSource(lambda: LambdaFunctionConstruct, queue: sqs.Queue): void {
    lambda.function.addEventSource(new lambdaEventSources.SqsEventSource(queue, {
      batchSize: 1,
    }));
  }

  // Create CloudFormation outputs
  private createOutputs(lambda: LambdaFunctionConstruct, queue: sqs.Queue): void {
    new cdk.CfnOutput(this, 'LambdaFunctionName', {
      value: lambda.function.functionName,
      description: 'Lambda Function Name',
    });

    new cdk.CfnOutput(this, 'LambdaFunctionArn', {
      value: lambda.function.functionArn,
      description: 'Lambda Function ARN',
    });

    new cdk.CfnOutput(this, 'QueueUrl', {
      value: queue.queueUrl,
      description: 'SQS Queue URL',
    });

    new cdk.CfnOutput(this, 'QueueArn', {
      value: queue.queueArn,
      description: 'SQS Queue ARN',
    });
  }

  // Helper method to get SSM parameter values
  private getParameter(paramName: string): string {
    return ssm.StringParameter.valueForStringParameter(this, paramName);
  }
}