import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';
import { EnvironmentConfigStack } from '../../config/environment-config';

interface FrStackProps extends cdk.StackProps {
  envStack: EnvironmentConfigStack;
}

export class FrStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: FrStackProps) {
    super(scope, id, props);

    const { envStack } = props;
    const { baseConfig, parserConfig, vpcConfig } = envStack;

    // Create SQS Queue
    const queue = new sqs.Queue(this, 'FrQueue', {
      queueName: `${baseConfig.stackPrefix}-fr-queue`,
      visibilityTimeout: cdk.Duration.seconds(parserConfig.queueVisibilityTimeout),
      retentionPeriod: cdk.Duration.days(parserConfig.queueRetentionDays),
    });

    // Create Lambda Role
    const lambdaRole = new iam.Role(this, 'FrLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: envStack.iamConfig.path,
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy${envStack.iamConfig.permissionsBoundaryPolicy}`
      ),
    });

    // Add Lambda permissions
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['sqs:*'],
        resources: [queue.queueArn],
      })
    );

    // Create Lambda Function
    const parser = new lambda.DockerImageFunction(this, 'FrFunction', {
      functionName: `${baseConfig.stackPrefix}-fr-function`,
      code: lambda.DockerImageCode.fromImageAsset('../../../solution/parser/fr-parser'),
      timeout: cdk.Duration.seconds(parserConfig.timeout),
      memorySize: parserConfig.memorySize,
      vpc: ec2.Vpc.fromVpcAttributes(this, 'ImportedVpc', {
        vpcId: vpcConfig.vpcId,
        availabilityZones: ['us-east-1a', 'us-east-1b'],
        privateSubnetIds: vpcConfig.privateSubnetIds,
      }),
      role: lambdaRole,
      environment: {
        STAGE: baseConfig.environment,
        QUEUE_URL: queue.queueUrl,
      },
    });

    // Add stack tags
    Object.entries(baseConfig.tags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });
  }
}