import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_lambda as lambda,
  aws_apigateway as apigateway,
  aws_logs as logs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

export interface ApiConstructProps {
  vpc: ec2.IVpc;
  securityGroup: ec2.SecurityGroup;
  environmentVariables: Record<string, string>;
  storageBucketName: string;
  queueUrl: string;
  lambdaConfig: {
    memorySize: number;
    timeout: number;
    reservedConcurrentExecutions?: number;
  };
  stageConfig: StageConfig;
  vpcSubnets: ec2.SubnetSelection;
  lambda: lambda.Function;
  authorizerLambda?: lambda.Function;
}

export class ApiConstruct extends Construct {
  public readonly api: apigateway.RestApi;
  public readonly lambda: lambda.Function;

  constructor(scope: Construct, id: string, props: ApiConstructProps) {
    super(scope, id);

    // Store the Lambda reference
    this.lambda = props.lambda;

    // Create API Gateway log group
    const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: props.stageConfig.aws.apiGateway('api'),
      retention: logs.RetentionDays.ONE_MONTH,
    });

    // Use getResourceName to get the correct stage name
    // This will automatically handle both ephemeral and regular environments
    // Determine stage name based on environment type
    const stageName = props.stageConfig.isEphemeral() 
    ? props.stageConfig.getResourceName('').split('-').slice(0, 2).join('-') // Gets 'eph-123' from 'cms-eregs-eph-123-'
    : props.stageConfig.environment; // Gets 'dev', 'val', or 'prod'

    // Create authorizer if Lambda is provided (non-prod environments)
    let authorizer: apigateway.IAuthorizer | undefined;
    if (props.authorizerLambda) {
      authorizer = new apigateway.TokenAuthorizer(this, 'BasicAuthAuthorizer', {
        handler: props.authorizerLambda,
        identitySource: 'method.request.header.Authorization',
      });
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
      responseHeaders: {
        'WWW-Authenticate': "'Basic'",
        'Access-Control-Allow-Origin': "'*'",
      },
      statusCode: '401',
    });

    // Add CORS for all methods
    this.addCorsOptions(this.api.root);
  }

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
