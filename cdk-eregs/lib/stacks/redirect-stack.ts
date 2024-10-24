// lib/stacks/redirect-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import { Construct } from 'constructs';
import { EnvironmentConfigStack } from '../../config/environment-config';

interface RedirectStackProps extends cdk.StackProps {
  envStack: EnvironmentConfigStack;
}

export class RedirectStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: RedirectStackProps) {
    super(scope, id, props);

    const { envStack } = props;
    const { baseConfig, iamConfig, redirectConfig, commonConfig } = envStack;

    // Create IAM Role for Lambda
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: iamConfig.path,
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy${iamConfig.permissionsBoundaryPolicy}`
      ),
    });

    // Add CloudWatch Logs permissions
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
      })
    );

    // Create Lambda Function
    const redirectLambda = new lambda.Function(this, 'RedirectFunction', {
      functionName: `${baseConfig.stackPrefix}-redirectFunction`,
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'redirect_lambda.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')),
      timeout: cdk.Duration.seconds(baseConfig.isExperimental ? 30 : 60),
      memorySize: baseConfig.isExperimental ? 128 : 256,
      environment: {
        STAGE: commonConfig.stage,
        LOG_LEVEL: commonConfig.logLevel,
        HTTP_USER: redirectConfig.httpUser,
        HTTP_PASSWORD: redirectConfig.httpPassword,
      },
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
    });

    // Create CloudWatch Role for API Gateway
    const apiGatewayCloudWatchRole = new iam.Role(this, 'ApiGatewayCloudWatchRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      path: iamConfig.path,
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonAPIGatewayPushToCloudWatchLogs'),
      ],
    });

    // Create API Gateway Account settings
    new apigateway.CfnAccount(this, 'ApiGatewayAccount', {
      cloudWatchRoleArn: apiGatewayCloudWatchRole.roleArn,
    });

    // Create API Gateway
    const api = new apigateway.RestApi(this, 'RedirectApi', {
      deployOptions: {
        stageName: redirectConfig.apiStageName,
        tracingEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      },
      binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
    });

    // Add proxy resource to API Gateway
    api.root.addProxy({
      defaultIntegration: new apigateway.LambdaIntegration(redirectLambda),
      anyMethod: true,
    });

    // Add stack tags
    Object.entries(baseConfig.tags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });

    // Outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL',
    });
  }
}