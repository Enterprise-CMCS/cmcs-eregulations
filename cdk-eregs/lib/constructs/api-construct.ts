import * as cdk from 'aws-cdk-lib';
import {
 aws_ec2 as ec2,
 aws_lambda as lambda,
 aws_apigateway as apigateway,
 aws_logs as logs,
 aws_iam as iam,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

/**
* Props for the ApiConstruct
* @interface ApiConstructProps
*/
export interface ApiConstructProps {
 /** VPC configuration */
 vpc: ec2.IVpc;
 /** Security group for the API */
 securityGroup: ec2.SecurityGroup;
 /** Environment variables for Lambda functions */
 environmentVariables: Record<string, string>;
 /** S3 bucket name for storage */
 storageBucketName: string;
 /** SQS queue URL */
 queueUrl: string;
 /** Lambda function configuration */
 lambdaConfig: {
   memorySize: number;
   timeout: number;
   reservedConcurrentExecutions?: number;
 };
 /** Stage configuration object */
 stageConfig: StageConfig;
 /** VPC subnet selection */
 vpcSubnets: ec2.SubnetSelection;
 /** Main Lambda function */
 lambda: lambda.Function;
 /** Optional authorizer Lambda function */
 authorizerLambda?: lambda.Function;
}

/**
* Construct for API Gateway with Lambda integration and optional authorization
* @class ApiConstruct
*/
export class ApiConstruct extends Construct {
 /** The API Gateway REST API */
 public readonly api: apigateway.RestApi;
 /** The main Lambda function */
 public readonly lambda: lambda.Function;

 /**
  * Creates a new API Gateway construct
  * @param scope The scope of the construct
  * @param id The ID of the construct
  * @param props The properties for the construct
  */
 constructor(scope: Construct, id: string, props: ApiConstructProps) {
   super(scope, id);

   this.lambda = props.lambda;

   // Create API Gateway log group
   const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
     logGroupName: props.stageConfig.aws.apiGateway('api'),
     retention: logs.RetentionDays.ONE_MONTH,
   });

   // Determine stage name based on environment type
   const stageName = props.stageConfig.isEphemeral() 
     ? props.stageConfig.getResourceName('')
         .replace(`${StageConfig.projectName}-`, '')
         .split('-resource')[0]
         .replace(/-$/, '')
     : props.stageConfig.environment;

   // Create request authorizer if Lambda is provided (non-prod environments)
   let authorizer: apigateway.IAuthorizer | undefined;
   if (props.authorizerLambda) {
     authorizer = new apigateway.RequestAuthorizer(this, 'ApiGatewayAuthorizer', {
       handler: props.authorizerLambda,
       identitySources: [apigateway.IdentitySource.header('Authorization')],
       authorizerName: props.stageConfig.getResourceName('authorizer'),
       resultsCacheTtl: cdk.Duration.seconds(0),
     });

     // Add permission for API Gateway to invoke the authorizer
     props.authorizerLambda.addPermission('ApiGatewayInvoke', {
       principal: new iam.ServicePrincipal('apigateway.amazonaws.com'),
       sourceArn: cdk.Fn.join(':', [
         'arn:aws:execute-api',
         cdk.Stack.of(this).region,
         cdk.Stack.of(this).account,
         `${this.api.restApiId}/authorizers/*`
       ])
     });

     // Add required environment variables to the authorizer
     props.authorizerLambda.addEnvironment('HTTP_AUTH_USER', props.environmentVariables.HTTP_AUTH_USER);
     props.authorizerLambda.addEnvironment('HTTP_AUTH_PASSWORD', props.environmentVariables.HTTP_AUTH_PASSWORD);
   }

   // Create API Gateway
   this.api = new apigateway.RestApi(this, 'API', {
     restApiName: props.stageConfig.getResourceName('api'),
     description: 'eRegulations API Gateway',
     deployOptions: {
       stageName: stageName,
       loggingLevel: apigateway.MethodLoggingLevel.INFO,
       dataTraceEnabled: true,
       accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
       accessLogFormat: apigateway.AccessLogFormat.clf(),
       metricsEnabled: true,
       tracingEnabled: true,
     },
     binaryMediaTypes: [
       'multipart/form-data',
       'application/pdf',
       'application/json',
       'application/octet-stream',
       'image/*',
     ],
   });

   // Add Lambda integration
   const integration = new apigateway.LambdaIntegration(this.lambda, {
     proxy: true,
     allowTestInvoke: true,
   });

   // Configure method options based on whether auth is required
   const methodOptions: apigateway.MethodOptions = {
     apiKeyRequired: false,
     authorizer: authorizer,
     authorizationType: props.authorizerLambda 
       ? apigateway.AuthorizationType.CUSTOM 
       : apigateway.AuthorizationType.NONE,
   };

   // Add root path with conditional auth
   this.api.root.addMethod('ANY', integration, methodOptions);

   // Add proxy path for all other routes with conditional auth
   this.api.root.addProxy({
     defaultIntegration: integration,
     defaultMethodOptions: methodOptions,
     anyMethod: true,
   });

// Add customized 401 response
new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
  restApi: this.api,
  type: apigateway.ResponseType.UNAUTHORIZED,
  responseHeaders: {  // Changed from responseParameters
    'gatewayresponse.header.WWW-Authenticate': "'Basic'",
    'gatewayresponse.header.Access-Control-Allow-Origin': "'*'",
  },
  statusCode: '401',
});

   // Add CORS support
   this.addCorsOptions(this.api.root);
 }

 /**
  * Adds CORS options to an API resource
  * @param apiResource The API resource to add CORS options to
  * @private
  */
 private addCorsOptions(apiResource: apigateway.IResource) {
   apiResource.addMethod(
     'OPTIONS',
     new apigateway.MockIntegration({
       integrationResponses: [
         {
           statusCode: '200',
           responseParameters: {
             'method.response.header.Access-Control-Allow-Headers':
               "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
             'method.response.header.Access-Control-Allow-Origin': "'*'",
             'method.response.header.Access-Control-Allow-Methods':
               "'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD'",
           },
         },
       ],
       passthroughBehavior: apigateway.PassthroughBehavior.NEVER,
       requestTemplates: {
         'application/json': '{"statusCode": 200}',
       },
     }),
     {
       methodResponses: [
         {
           statusCode: '200',
           responseParameters: {
             'method.response.header.Access-Control-Allow-Headers': true,
             'method.response.header.Access-Control-Allow-Methods': true,
             'method.response.header.Access-Control-Allow-Origin': true,
           },
         },
       ],
     }
   );
 }
}
// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_lambda as lambda,
//   aws_apigateway as apigateway,
//   aws_logs as logs,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';

// export interface ApiConstructProps {
//   vpc: ec2.IVpc;
//   securityGroup: ec2.SecurityGroup;
//   environmentVariables: Record<string, string>;
//   storageBucketName: string;
//   queueUrl: string;
//   lambdaConfig: {
//     memorySize: number;
//     timeout: number;
//     reservedConcurrentExecutions?: number;
//   };
//   stageConfig: StageConfig;
//   vpcSubnets: ec2.SubnetSelection;
//   lambda: lambda.Function;
//   authorizerLambda?: lambda.Function;
// }

// export class ApiConstruct extends Construct {
//   public readonly api: apigateway.RestApi;
//   public readonly lambda: lambda.Function;

//   constructor(scope: Construct, id: string, props: ApiConstructProps) {
//     super(scope, id);

//     // Store the Lambda reference
//     this.lambda = props.lambda;

//     // Create API Gateway log group
//     const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
//       logGroupName: props.stageConfig.aws.apiGateway('api'),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

// // Determine stage name based on environment type
//     const stageName = props.stageConfig.isEphemeral() 
//       ? props.stageConfig.getResourceName('')
//           .replace(`${StageConfig.projectName}-`, '')
//           .split('-resource')[0]
//           .replace(/-$/, '')  // Remove trailing dash
//       : props.stageConfig.environment;
//     // Create authorizer if Lambda is provided (non-prod environments)
//     let authorizer: apigateway.IAuthorizer | undefined;
//     if (props.authorizerLambda) {
//       authorizer = new apigateway.TokenAuthorizer(this, 'BasicAuthAuthorizer', {
//         handler: props.authorizerLambda,
//         identitySource: 'method.request.header.Authorization',
//       });
//     }

//     // Create API Gateway
//     this.api = new apigateway.RestApi(this, 'API', {
//       restApiName: props.stageConfig.getResourceName('api'),
//       description: 'eRegulations API Gateway',
//       deployOptions: {
//         stageName: stageName,
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
//         accessLogFormat: apigateway.AccessLogFormat.clf(),
//         metricsEnabled: true,
//         tracingEnabled: true,
//       },
//       binaryMediaTypes: [
//         'multipart/form-data',
//         'application/pdf',
//         'application/json',
//         'application/octet-stream',
//         'image/*',
//       ],
//     });

//     // Add Lambda integration
//     const integration = new apigateway.LambdaIntegration(this.lambda, {
//       proxy: true,
//       allowTestInvoke: true,
//     });

//     // Configure method options based on whether auth is required
//     const methodOptions: apigateway.MethodOptions = {
//       apiKeyRequired: false, 
//       authorizer: authorizer,
//       authorizationType: props.authorizerLambda 
//         ? apigateway.AuthorizationType.CUSTOM 
//         : apigateway.AuthorizationType.NONE,
//     };

//     // Add root path with conditional auth
//     this.api.root.addMethod('ANY', integration, methodOptions);

//     // Add proxy path for all other routes with conditional auth
//     this.api.root.addProxy({
//       defaultIntegration: integration,
//       defaultMethodOptions: methodOptions,
//       anyMethod: true,
//     });
   
//     // Add customized 401 response
//     new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
//       restApi: this.api,
//       type: apigateway.ResponseType.UNAUTHORIZED,
//       responseHeaders: {
//         'WWW-Authenticate': "'Basic'",
//         'Access-Control-Allow-Origin': "'*'",
//       },
//       statusCode: '401',
//     });

//     // Add CORS for all methods
//     this.addCorsOptions(this.api.root);
//   }

//   private addCorsOptions(apiResource: apigateway.IResource) {
//     apiResource.addMethod(
//       'OPTIONS',
//       new apigateway.MockIntegration({
//         integrationResponses: [
//           {
//             statusCode: '200',
//             responseParameters: {
//               'method.response.header.Access-Control-Allow-Headers':
//                 "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
//               'method.response.header.Access-Control-Allow-Origin': "'*'",
//               'method.response.header.Access-Control-Allow-Methods':
//                 "'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD'",
//             },
//           },
//         ],
//         passthroughBehavior: apigateway.PassthroughBehavior.NEVER,
//         requestTemplates: {
//           'application/json': '{"statusCode": 200}',
//         },
//       }),
//       {
//         methodResponses: [
//           {
//             statusCode: '200',
//             responseParameters: {
//               'method.response.header.Access-Control-Allow-Headers': true,
//               'method.response.header.Access-Control-Allow-Methods': true,
//               'method.response.header.Access-Control-Allow-Origin': true,
//             },
//           },
//         ],
//       }
//     );
//   }
// }
// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_lambda as lambda,
//   aws_apigateway as apigateway,
//   aws_logs as logs,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';

// export interface ApiConstructProps {
//   vpc: ec2.IVpc;
//   securityGroup: ec2.SecurityGroup;
//   environmentVariables: Record<string, string>;
//   storageBucketName: string;
//   queueUrl: string;
//   lambdaConfig: {
//     memorySize: number;
//     timeout: number;
//     reservedConcurrentExecutions?: number;
//   };
//   stageConfig: StageConfig;
//   vpcSubnets: ec2.SubnetSelection;
//   lambda: lambda.Function;
//   authorizerLambda?: lambda.Function;
// }

// export class ApiConstruct extends Construct {
//   public readonly api: apigateway.RestApi;
//   public readonly lambda: lambda.Function;

//   constructor(scope: Construct, id: string, props: ApiConstructProps) {
//     super(scope, id);

//     // Store the Lambda reference
//     this.lambda = props.lambda;

//     // Create API Gateway log group
//     const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
//       logGroupName: props.stageConfig.aws.apiGateway('api'),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

//     // Create authorizer if Lambda is provided
//     let authorizer: apigateway.IAuthorizer | undefined;
//     if (props.authorizerLambda) {
//       authorizer = new apigateway.TokenAuthorizer(this, 'BasicAuthAuthorizer', {
//         handler: props.authorizerLambda,
//         identitySource: 'method.request.header.Authorization',
//       });
//     }

//     // Create API Gateway
//     this.api = new apigateway.RestApi(this, 'API', {
//       restApiName: props.stageConfig.getResourceName('api'),
//       description: 'eRegulations API Gateway',
//       deployOptions: {
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
//         accessLogFormat: apigateway.AccessLogFormat.clf(),
//         metricsEnabled: true,
//         tracingEnabled: true,
//       },
//       binaryMediaTypes: [
//         'multipart/form-data',
//         'application/pdf',
//         'application/json',
//         'application/octet-stream',
//         'image/*',
//       ],
//     });

//     // Add Lambda integration
//     const integration = new apigateway.LambdaIntegration(this.lambda, {
//       proxy: true,
//       allowTestInvoke: true,
//     });

//     // Configure method options based on whether auth is required
//     const methodOptions: apigateway.MethodOptions = {
//       authorizer: authorizer,
//       authorizationType: props.authorizerLambda 
//         ? apigateway.AuthorizationType.CUSTOM 
//         : apigateway.AuthorizationType.NONE,
//     };

//     // Add root path with conditional auth
//     this.api.root.addMethod('ANY', integration, methodOptions);

//     // Add proxy path for all other routes with conditional auth
//     this.api.root.addProxy({
//       defaultIntegration: integration,
//       defaultMethodOptions: methodOptions,
//       anyMethod: true,
//     });

//     // Add customized 401 response
//     new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
//       restApi: this.api,
//       type: apigateway.ResponseType.UNAUTHORIZED,
//       responseHeaders: {
//         'WWW-Authenticate': "'Basic'",
//         'Access-Control-Allow-Origin': "'*'",
//       },
//       statusCode: '401',
//     });

//     // Add CORS for all methods
//     this.addCorsOptions(this.api.root);
//   }

//   private addCorsOptions(apiResource: apigateway.IResource) {
//     apiResource.addMethod('OPTIONS', new apigateway.MockIntegration({
//       integrationResponses: [{
//         statusCode: '200',
//         responseParameters: {
//           'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
//           'method.response.header.Access-Control-Allow-Origin': "'*'",
//           'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD'",
//         },
//       }],
//       passthroughBehavior: apigateway.PassthroughBehavior.NEVER,
//       requestTemplates: {
//         "application/json": "{\"statusCode\": 200}"
//       },
//     }), {
//       methodResponses: [{
//         statusCode: '200',
//         responseParameters: {
//           'method.response.header.Access-Control-Allow-Headers': true,
//           'method.response.header.Access-Control-Allow-Methods': true,
//           'method.response.header.Access-Control-Allow-Origin': true,
//         },
//       }]
//     });
//   }
// }
