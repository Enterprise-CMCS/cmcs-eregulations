// import * as cdk from 'aws-cdk-lib';
// import * as apigateway from 'aws-cdk-lib/aws-apigateway';
// import * as iam from 'aws-cdk-lib/aws-iam';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as path from 'path';
// import { Construct } from 'constructs';
// import { EnvironmentConfig } from '../../config/environment-config';
// import { SsmParameterStack } from './ssm-parameter-stack';

// export class RedirectStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props?: cdk.StackProps) {
//     super(scope, id, props);

//     const stage = this.node.tryGetContext('stage') || 'dev';

//     // Create the SSM Parameter Stack
//     const ssmStack = new SsmParameterStack(this, 'SsmParameterStack', { stage });

//     // Create the EnvironmentConfig with SSM values
//     const config = new EnvironmentConfig(stage,);
//     // config.iamPath = ssmStack.ssmParameters.iamPath;
//     // config.permissionsBoundaryPolicy = ssmStack.ssmParameters.permissionsBoundaryPolicy;

//     // Create IAM Role for Lambda
//     const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       path: config.iamPath,
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
//       ],
//     //   permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//     //     this,
//     //     'PermissionsBoundary',
//     //     `arn:aws:iam::${this.account}:policy${config.permissionsBoundaryPolicy}`
//     //   ),
//     });

//     // Add inline policy for CloudWatch Logs
//     lambdaRole.addToPolicy(
//       new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
//         resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
//       })
//     );
//    // Create Lambda Function - Packaging `redirect_lambda.py`
//    const redirectLambda = new lambda.Function(this, 'RedirectFunction', {
//     functionName: `${config.stackPrefix}-redirectFunction`,
//     runtime: lambda.Runtime.PYTHON_3_9,
//     handler: 'redirect_lambda.handler', // Filename and function name within the file
//     code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')), // Point to the directory containing `redirect_lambda.py`
//     timeout: cdk.Duration.seconds(30),
//     memorySize: 128,
//     environment: {
//       STAGE: config.stackPrefix,
//     },
//     role: lambdaRole,
//     tracing: lambda.Tracing.ACTIVE, // Enables X-Ray tracing
//   });
//     // Create API Gateway
//     const api = new apigateway.RestApi(this, 'RedirectApi', {
//       deployOptions: {
//         tracingEnabled: true,
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         metricsEnabled: true,
//       },
//       binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
//     });

//     // Add proxy resource to API Gateway
//     api.root.addProxy({
//       defaultIntegration: new apigateway.LambdaIntegration(redirectLambda),
//       anyMethod: true,
//     });
//   }
// }
// import * as cdk from 'aws-cdk-lib';
// import * as apigateway from 'aws-cdk-lib/aws-apigateway';
// import * as iam from 'aws-cdk-lib/aws-iam';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as path from 'path';
// import { Construct } from 'constructs';
// import { SsmParameters } from '../../config/environment-config';

// interface RedirectStackProps extends cdk.StackProps {
//   ssmParameters: SsmParameters;
//   lambdaConfig: {
//     memorySize: number;
//     timeout: cdk.Duration;
//     environment: Record<string, string>;
//   };
//   apiGatewayConfig: {
//     deployOptions: apigateway.StageOptions;
//   };
// }

// export class RedirectStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: RedirectStackProps) {
//     super(scope, id, props);

//     const { ssmParameters, lambdaConfig, apiGatewayConfig } = props;

//     // Create IAM Role for Lambda
//     const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       path: ssmParameters.iamPath,
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
//       ],
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'PermissionsBoundary',
//         `arn:aws:iam::${this.account}:policy${ssmParameters.permissionsBoundaryPolicy}`
//       ),
//     });

//     // Add inline policy for CloudWatch Logs
//     lambdaRole.addToPolicy(
//       new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
//         resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
//       })
//     );

//     // Create Lambda Function
//     const redirectLambda = new lambda.Function(this, 'RedirectFunction', {
//       runtime: lambda.Runtime.PYTHON_3_9,
//       handler: 'redirect_lambda.handler',
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')),
//       timeout: lambdaConfig.timeout,
//       memorySize: lambdaConfig.memorySize,
//       environment: {
//         ...lambdaConfig.environment,
//         HTTP_USER: ssmParameters.httpUser,
//         HTTP_PASSWORD: ssmParameters.httpPassword,
//       },
//       role: lambdaRole,
//       tracing: lambda.Tracing.ACTIVE,
//     });

//     // Create API Gateway
//     const api = new apigateway.RestApi(this, 'RedirectApi', {
//       deployOptions: {
//         ...apiGatewayConfig.deployOptions,
//         tracingEnabled: true,
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         metricsEnabled: true,
//       },
//       binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
//     });

//     // Add proxy resource to API Gateway
//     api.root.addProxy({
//       defaultIntegration: new apigateway.LambdaIntegration(redirectLambda),
//       anyMethod: true,
//     });

//     // Add CloudWatch API Gateway Logging Role
//     api.addToLogicalId('Account').addToResourcePolicy(
//       new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         principals: [new iam.ServicePrincipal('apigateway.amazonaws.com')],
//         actions: ['cloudwatch:PutMetricData'],
//         resources: ['*'],
//       })
//     );

//     // Output the API URL
//     new cdk.CfnOutput(this, 'ApiEndpoint', {
//       value: api.url,
//       description: 'API Gateway endpoint URL',
//     });
//   }
// }

// lib/stacks/redirect-stack.ts
// import * as cdk from 'aws-cdk-lib';
// import * as apigateway from 'aws-cdk-lib/aws-apigateway';
// import * as iam from 'aws-cdk-lib/aws-iam';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as path from 'path';
// import { Construct } from 'constructs';
// import { SsmParameters } from '../../config/environment-config';

// interface RedirectStackProps extends cdk.StackProps {
//   ssmParameters: SsmParameters;
//   lambdaConfig: {
//     memorySize: number;
//     timeout: cdk.Duration;
//     environment: Record<string, string>;
//   };
//   apiGatewayConfig: {
//     deployOptions: apigateway.StageOptions;
//   };
// }

// export class RedirectStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: RedirectStackProps) {
//     super(scope, id, props);

//     const { ssmParameters, lambdaConfig, apiGatewayConfig } = props;

//     // Create IAM Role for Lambda
//     const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       path: ssmParameters.iamPath,
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
//       ],
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'PermissionsBoundary',
//         `arn:aws:iam::${this.account}:policy${ssmParameters.permissionsBoundaryPolicy}`
//       ),
//     });

//     // Add inline policy for CloudWatch Logs
//     lambdaRole.addToPolicy(
//       new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
//         resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
//       })
//     );

//     // Create Lambda Function
//     const redirectLambda = new lambda.Function(this, 'RedirectFunction', {
//       runtime: lambda.Runtime.PYTHON_3_9,
//       handler: 'redirect_lambda.handler',
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')),
//       timeout: lambdaConfig.timeout,
//       memorySize: lambdaConfig.memorySize,
//       environment: {
//         ...lambdaConfig.environment,
//         HTTP_USER: ssmParameters.httpUser,
//         HTTP_PASSWORD: ssmParameters.httpPassword,
//       },
//       role: lambdaRole,
//       tracing: lambda.Tracing.ACTIVE,
//     });

//     // Create CloudWatch Role for API Gateway
//     const apiGatewayCloudWatchRole = new iam.Role(this, 'ApiGatewayCloudWatchRole', {
//       assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
//       path: ssmParameters.iamPath,
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonAPIGatewayPushToCloudWatchLogs'),
//       ],
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'ApiGatewayPermissionsBoundary',
//         `arn:aws:iam::${this.account}:policy${ssmParameters.permissionsBoundaryPolicy}`
//       ),
//     });

//     // Create API Gateway Account settings
//     new apigateway.CfnAccount(this, 'ApiGatewayAccount', {
//       cloudWatchRoleArn: apiGatewayCloudWatchRole.roleArn,
//     });

//     // Create API Gateway
//     const api = new apigateway.RestApi(this, 'RedirectApi', {
//       deployOptions: {
//         ...apiGatewayConfig.deployOptions,
//         tracingEnabled: true,
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         metricsEnabled: true,
//       },
//       binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
//     });

//     // Add proxy resource to API Gateway
//     api.root.addProxy({
//       defaultIntegration: new apigateway.LambdaIntegration(redirectLambda),
//       anyMethod: true,
//     });

//     // Outputs
//     new cdk.CfnOutput(this, 'ApiEndpoint', {
//       value: api.url,
//       description: 'API Gateway endpoint URL',
//     });
//   }
// }
// lib/stacks/redirect-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import { Construct } from 'constructs';
import { EnvironmentConfigStack} from '../../config/environment-config';
// import { EnvironmentStack } from '../../config/environment-config';

interface RedirectStackProps extends cdk.StackProps {
  envStack: EnvironmentStack;
}

export class RedirectStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: RedirectStackProps) {
    super(scope, id, props);

    const { envStack } = props;
    const config = envStack.config;

    // Create IAM Role for Lambda
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: envStack.getSsmValue('iamPath'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy${envStack.getSsmValue('permissionsBoundaryPolicy')}`
      ),
    });

    // Add inline policy for CloudWatch Logs
    lambdaRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
      })
    );

    // Create Lambda Function
    const redirectLambda = new lambda.Function(this, 'RedirectFunction', {
      functionName: `${config.stackPrefix}-redirectFunction`,
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'redirect_lambda.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')),
      timeout: cdk.Duration.seconds(config.isExperimental ? 30 : 60),
      memorySize: config.isExperimental ? 128 : 256,
      environment: {
        STAGE: config.stage,
        LOG_LEVEL: envStack.getSsmValue('logLevel'),
        HTTP_USER: envStack.getSsmValue('httpUser'),
        HTTP_PASSWORD: envStack.getSsmValue('httpPassword'),
      },
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
    });

    // Create CloudWatch Role for API Gateway
    const apiGatewayCloudWatchRole = new iam.Role(this, 'ApiGatewayCloudWatchRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      path: envStack.getSsmValue('iamPath'),
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
        stageName: config.isExperimental ? 'exp' : config.stage,
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

    // Outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL',
    });
  }
}