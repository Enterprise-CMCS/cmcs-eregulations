// lib/stacks/redirect-api-stack.ts
import * as cdk from 'aws-cdk-lib';
import {
  aws_iam as iam,
  aws_logs as logs,
  aws_lambda as lambda,
  aws_apigateway as apigateway,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

/**
 * Configuration for the Lambda function
 */
interface LambdaConfig {
  runtime: lambda.Runtime;
  memorySize: number;
  timeout: number;
  handler?: string;
  codePath?: string;
}

/**
 * Configuration for the API Gateway
 */
interface ApiGatewayConfig {
  binaryMediaTypes?: string[];
  endpointType?: apigateway.EndpointType;
  loggingLevel?: apigateway.MethodLoggingLevel;
}

/**
 * Properties for the RedirectApiStack
 */
export interface RedirectApiStackProps extends cdk.StackProps {
  lambdaConfig: LambdaConfig;
  apiConfig?: ApiGatewayConfig;
}

const DEFAULT_API_CONFIG: ApiGatewayConfig = {
  binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
  endpointType: apigateway.EndpointType.EDGE,
  loggingLevel: apigateway.MethodLoggingLevel.INFO,
};

export class RedirectApiStack extends cdk.Stack {
  public readonly lambdaFunction: lambda.Function;
  public readonly api: apigateway.RestApi;
  private readonly stageConfig: StageConfig;

  constructor(
    scope: Construct, 
    id: string, 
    props: RedirectApiStackProps,
    stageConfig: StageConfig
  ) {
    super(scope, id, props);
    this.stageConfig = stageConfig;

    const apiConfig = { ...DEFAULT_API_CONFIG, ...props.apiConfig };

    const { lambdaRole, logGroup } = this.createLambdaInfrastructure();
    this.lambdaFunction = this.createLambdaFunction(lambdaRole, logGroup, props.lambdaConfig);
    this.api = this.createApiGateway(apiConfig);
    this.configureApiGateway();
    this.createStackOutputs();
  }

  private createLambdaInfrastructure() {
    // Lambda CloudWatch Log Group
    const logGroup = new logs.LogGroup(this, 'RedirectFunctionLogGroup', {
      logGroupName: this.stageConfig.aws.lambda('redirect-function'),
      retention: logs.RetentionDays.INFINITE,
    });

    // Lambda IAM Role
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      inlinePolicies: {
        LambdaPolicy: this.createLambdaPolicy(),
      },
    });

    return { lambdaRole, logGroup };
  }

  private createLambdaPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
          resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
        }),
      ],
    });
  }

  private createLambdaFunction(
    role: iam.Role,
    logGroup: logs.LogGroup,
    config: LambdaConfig,
  ): lambda.Function {
    return new lambda.Function(this, 'RedirectFunctionLambdaFunction', {
      functionName: this.stageConfig.getResourceName('redirect-function'),
      description: `Redirect API Lambda function for ${this.stageConfig.environment} stage`,
      runtime: config.runtime,
      handler: config.handler ?? 'redirect_lambda.handler',
      code: lambda.Code.fromAsset(config.codePath ?? '../solution/backend/'),
      memorySize: config.memorySize,
      timeout: cdk.Duration.seconds(config.timeout),
      role,
      environment: {
        STAGE: this.stageConfig.environment,
        APP_NAME: StageConfig.projectName,
      },
    });
  }

  private createApiGateway(config: ApiGatewayConfig): apigateway.RestApi {
    const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
      restApiName: this.stageConfig.getResourceName('api-gateway'),
      description: `API Gateway for ${StageConfig.projectName} ${this.stageConfig.environment}`,
      binaryMediaTypes: config.binaryMediaTypes,
      endpointConfiguration: {
        types: [config.endpointType!],
      },
      deployOptions: {
        stageName: this.stageConfig.environment,
        loggingLevel: config.loggingLevel,
      },
    });

    // API Gateway Log Group
    new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: this.stageConfig.aws.apiGateway('api-gateway'),
    });

    return api;
  }

  private configureApiGateway() {
    const integration = new apigateway.LambdaIntegration(this.lambdaFunction, { proxy: true });
    
    this.api.root.addMethod('ANY', integration, { 
      apiKeyRequired: false, 
      methodResponses: [{ statusCode: '200' }] 
    });
    
    const proxyResource = this.api.root.addResource('{proxy+}');
    proxyResource.addMethod('ANY', integration, { 
      apiKeyRequired: false, 
      methodResponses: [{ statusCode: '200' }] 
    });
  }

  private createStackOutputs() {
    const outputs: Record<string, cdk.CfnOutputProps> = {
      RedirectFunctionLambdaFunctionQualifiedArn: {
        value: this.lambdaFunction.functionArn,
        description: 'Current Lambda function version',
        exportName: this.stageConfig.getResourceName('redirect-function-arn'),
      },
      ServiceEndpoint: {
        value: `https://${this.api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${this.stageConfig.environment}`,
        description: 'URL of the service endpoint',
        exportName: this.stageConfig.getResourceName('service-endpoint'),
      },
    };

    Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
  }
}

// // lib/redirect-api-stack.ts
// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_iam as iam,
//   aws_logs as logs,
//   aws_lambda as lambda,
//   aws_apigateway as apigateway,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { getResourceName } from '../../utils/naming-utils';
// import { StageConfig } from '../../config/stage-config';
// /**
//  * Configuration for the Lambda function, including runtime, memory, timeout, handler, and code path.
//  */
// interface LambdaConfig {
//   runtime: lambda.Runtime;
//   memorySize: number;
//   timeout: number;
//   handler?: string;
//   codePath?: string;
// }

// /**
//  * Configuration for the API Gateway, allowing customization of binary media types, endpoint type, and logging level.
//  */
// interface ApiGatewayConfig {
//   binaryMediaTypes?: string[];
//   endpointType?: apigateway.EndpointType;
//   loggingLevel?: apigateway.MethodLoggingLevel;
// }

// /**
//  * Properties for the RedirectApiStack, which includes stage, appName, lambdaConfig, and apiConfig.
//  * It also optionally accepts a prNumber for unique naming in ephemeral environments.
//  */
// export interface RedirectApiStackProps extends cdk.StackProps {
//   stage: string;
//   appName: string;
//   lambdaConfig: LambdaConfig;
//   apiConfig?: ApiGatewayConfig;
//   prNumber?: string; // Optional PR number to ensure unique resource names in ephemeral environments
// }

// // Default configurations for API Gateway
// const DEFAULT_API_CONFIG: ApiGatewayConfig = {
//   binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
//   endpointType: apigateway.EndpointType.EDGE,
//   loggingLevel: apigateway.MethodLoggingLevel.INFO,
// };

// /**
//  * CDK Stack for creating an API that redirects requests to a Lambda function.
//  * Configurable by Lambda and API Gateway properties, this stack includes Lambda, IAM, Logs, and API Gateway resources.
//  */
// export class RedirectApiStack extends cdk.Stack {
//   public readonly lambdaFunction: lambda.Function;
//   public readonly api: apigateway.RestApi;
//   private readonly stage: string;
//   private readonly appName: string;
//   private readonly prNumber?: string;
//   private readonly stageConfig: StageConfig; 

//   /**
//    * Initializes a new instance of the RedirectApiStack.
//    * @param scope - Scope within which this stack is defined.
//    * @param id - Identifier for this stack.
//    * @param props - Properties for configuring the stack.
//    */
//   constructor(scope: Construct, id: string, props: RedirectApiStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     this.stage = props.stage;
//     this.appName = props.appName;
//     this.prNumber = props.prNumber;
    
//     // Merge API config with defaults
//     const apiConfig = { ...DEFAULT_API_CONFIG, ...props.apiConfig };

//     // Set up infrastructure for Lambda, including role and log group
//     const { lambdaRole, logGroup } = this.createLambdaInfrastructure();
//     this.lambdaFunction = this.createLambdaFunction(lambdaRole, logGroup, props.lambdaConfig);

//     // Create API Gateway with integrated Lambda function
//     this.api = this.createApiGateway(apiConfig);

//     // Configure routes and permissions for API Gateway
//     this.configureApiGateway();

//     // Define stack outputs for easy access to function ARN and API endpoint
//     this.createStackOutputs();
//   }

//   /**
//    * Creates infrastructure components for the Lambda function, including IAM role and CloudWatch Log Group.
//    * @returns The IAM role and log group configured for Lambda.
//    */
//   private createLambdaInfrastructure() {
//     // CloudWatch Log Group for Lambda logs with consistent naming
//     const logGroup = new logs.LogGroup(this, 'RedirectFunctionLogGroup', {
//       logGroupName: `/aws/lambda/${getResourceName(this.appName, this.stage, 'redirectFunction', this.prNumber)}`,
//       retention: logs.RetentionDays.INFINITE,
//     });

//     // IAM role for Lambda, allowing access to necessary AWS resources
//     const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
//       ],
//       inlinePolicies: {
//         LambdaPolicy: this.createLambdaPolicy(),
//       },
//     });

//     return { lambdaRole, logGroup };
//   }

//   /**
//    * Creates the IAM policy for the Lambda function, granting permissions to write to CloudWatch Logs.
//    * @returns A policy document with permissions for log access.
//    */
//   private createLambdaPolicy(): iam.PolicyDocument {
//     return new iam.PolicyDocument({
//       statements: [
//         new iam.PolicyStatement({
//           effect: iam.Effect.ALLOW,
//           actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
//           resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
//         }),
//       ],
//     });
//   }

//   /**
//    * Creates and configures the Lambda function with the specified settings.
//    * @param role - The IAM role to associate with the Lambda function.
//    * @param logGroup - CloudWatch log group for the Lambda function's logs.
//    * @param config - Configuration properties for the Lambda function.
//    * @returns The Lambda function instance.
//    */
//   private createLambdaFunction(
//     role: iam.Role,
//     logGroup: logs.LogGroup,
//     config: LambdaConfig,
//   ): lambda.Function {
//     const functionName = getResourceName(this.appName, this.stage, 'redirectFunction', this.prNumber);

//     return new lambda.Function(this, 'RedirectFunctionLambdaFunction', {
//       functionName,
//       description: `Redirect API Lambda function for ${this.stage} stage`,
//       runtime: config.runtime,
//       handler: config.handler ?? 'redirect_lambda.handler',
//       code: lambda.Code.fromAsset(config.codePath ?? '../solution/backend/'),
//       memorySize: config.memorySize,
//       timeout: cdk.Duration.seconds(config.timeout),
//       role,
//       environment: {
//         STAGE: this.stage,
//         APP_NAME: this.appName,
//       },
//     });
//   }

//   /**
//    * Creates and configures an API Gateway REST API to route requests to the Lambda function.
//    * @param config - API Gateway configuration properties.
//    * @returns The API Gateway instance.
//    */
//   private createApiGateway(config: ApiGatewayConfig): apigateway.RestApi {
//     const apiName = getResourceName(this.appName, this.stage, 'apiGateway', this.prNumber);

//     const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
//       restApiName: apiName,
//       description: `API Gateway for ${this.appName} ${this.stage}`,
//       binaryMediaTypes: config.binaryMediaTypes,
//       endpointConfiguration: {
//         types: [config.endpointType!],
//       },
//       deployOptions: {
//         stageName: this.stage,
//         loggingLevel: config.loggingLevel,
//       },
//     });

//     // // API Gateway log group for access logs, using consistent naming
//     // new logs.LogGroup(this, 'ApiGatewayLogGroup', {
//     //   logGroupName: `/aws/api-gateway/${getResourceName(this.appName, this.stage, 'apiGatewayLogGroup', this.prNumber)}`,
//     // });
//     new logs.LogGroup(this, 'ApiGatewayLogGroup', {
//         logGroupName: `/aws/api-gateway/${stageConfig.getResourceName('api-gateway')}`,
//       });

//     return api;
//   }

//   /**
//    * Configures routes in the API Gateway to handle requests and pass them to the Lambda function.
//    */
//   private configureApiGateway() {
//     const integration = new apigateway.LambdaIntegration(this.lambdaFunction, { proxy: true });

//     // Root and proxy resources setup for handling all paths and methods
//     this.api.root.addMethod('ANY', integration, { apiKeyRequired: false, methodResponses: [{ statusCode: '200' }] });
//     const proxyResource = this.api.root.addResource('{proxy+}');
//     proxyResource.addMethod('ANY', integration, { apiKeyRequired: false, methodResponses: [{ statusCode: '200' }] });
//   }

//   /**
//    * Creates CloudFormation outputs for the stack, providing easy access to the Lambda ARN and API endpoint.
//    */
//   private createStackOutputs() {
//     const outputs: Record<string, cdk.CfnOutputProps> = {
//       RedirectFunctionLambdaFunctionQualifiedArn: {
//         value: this.lambdaFunction.functionArn,
//         description: 'Current Lambda function version',
//         exportName: getResourceName(this.appName, this.stage, 'RedirectFunctionLambdaFunctionQualifiedArn', this.prNumber),
//       },
//       ServiceEndpoint: {
//         value: `https://${this.api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${this.stage}`,
//         description: 'URL of the service endpoint',
//         exportName: getResourceName(this.appName, this.stage, 'ServiceEndpoint', this.prNumber),
//       },
//     };

//     // Define CloudFormation outputs
//     Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
//   }
// }

