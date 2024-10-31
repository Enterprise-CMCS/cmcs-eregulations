import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environment-config';
import { SsmParameterStack } from './ssm-parameter-stack';

export class HelloWorldStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const stage = this.node.tryGetContext('stage') || 'dev';
    const account = this.node.tryGetContext('account');
    const region = this.node.tryGetContext('region');

    // Create the SSM Parameter Stack
    const ssmStack = new SsmParameterStack(this, 'SsmParameterStack', { stage });

    // Create the EnvironmentConfig with SSM values
    const config = new EnvironmentConfig(stage, undefined);
    // config.iamPath = ssmStack.ssmParameters.iamPath;
    // config.permissionsBoundaryPolicy = ssmStack.ssmParameters.permissionsBoundaryPolicy;

    // Create IAM Role for Lambda
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: config.iamPath,
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
        //   permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        //     this,
        //     'PermissionsBoundary',
        //     `arn:aws:iam::${this.account}:policy${config.permissionsBoundaryPolicy}`
        //   ),
    });

    // Add inline policy for CloudWatch Logs
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: [`arn:aws:logs:${region}:${account}:log-group:/aws/lambda/*:*:*`],
      })
    );

    // Create Lambda Function - Packaging `hello_lambda.py`
    const helloLambda = new lambda.Function(this, 'HelloFunction', {
        functionName: `${stage}-helloFunction`,
        runtime: lambda.Runtime.PYTHON_3_9,
        handler: 'hello_lambda.handler', // Filename and function name within the file
        code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda')), // Point to the directory containing `hello_lambda.py`
        timeout: cdk.Duration.seconds(30),
        memorySize: 128,
        environment: {
        STAGE: config.stackPrefix,
        },
        role: lambdaRole,
        tracing: lambda.Tracing.ACTIVE, // Enables X-Ray tracing
    });

    const apiGateway = new apigateway.LambdaRestApi(this, `HelloWorldAPI`, {
        handler: helloLambda,
        proxy: false,
    });

    const helloResource = apiGateway.root.addResource('hello');
    helloResource.addMethod('GET');
  }
}
