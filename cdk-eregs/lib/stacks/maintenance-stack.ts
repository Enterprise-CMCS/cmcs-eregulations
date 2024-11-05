// lib/maintenance-api-stack.ts
import * as cdk from 'aws-cdk-lib';
import {
  aws_iam as iam,
  aws_logs as logs,
  aws_lambda as lambda,
  aws_apigateway as apigateway,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { getResourceName } from '../../utils/naming-utils';

/**
 * Configuration for the Lambda function, including runtime, memory, timeout, handler, and code path.
 */
interface LambdaConfig {
  runtime: lambda.Runtime;
  memorySize: number;
  timeout: number;
  handler?: string;
  codePath?: string;
}

/**
 * Configuration for the API Gateway, allowing customization of binary media types, endpoint type, and logging level.
 */
interface ApiGatewayConfig {
  binaryMediaTypes?: string[];
  endpointType?: apigateway.EndpointType;
  loggingLevel?: apigateway.MethodLoggingLevel;
}

/**
 * Properties for the MaintenanceApiStack, which includes stage, appName, lambdaConfig, and apiConfig.
 * It also optionally accepts a prNumber for unique naming in ephemeral environments.
 */
export interface MaintenanceApiStackProps extends cdk.StackProps {
  stage: string;
  appName: string;
  lambdaConfig: LambdaConfig;
  apiConfig?: ApiGatewayConfig;
  prNumber?: string; // Optional PR number to ensure unique resource names in ephemeral environments
}

// Default configurations for API Gateway
const DEFAULT_API_CONFIG: ApiGatewayConfig = {
  binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
  endpointType: apigateway.EndpointType.EDGE,
  loggingLevel: apigateway.MethodLoggingLevel.INFO,
};

/**
 * CDK Stack for creating an API that handles maintenance requests through a Lambda function.
 * Configurable by Lambda and API Gateway properties, this stack includes Lambda, IAM, Logs, and API Gateway resources.
 */
export class MaintenanceApiStack extends cdk.Stack {
  public readonly lambdaFunction: lambda.Function;
  public readonly api: apigateway.RestApi;
  private readonly stage: string;
  private readonly appName: string;
  private readonly prNumber?: string;

  /**
   * Initializes a new instance of the MaintenanceApiStack.
   * @param scope - Scope within which this stack is defined.
   * @param id - Identifier for this stack.
   * @param props - Properties for configuring the stack.
   */
  constructor(scope: Construct, id: string, props: MaintenanceApiStackProps) {
    super(scope, id, props);

    this.stage = props.stage;
    this.appName = props.appName;
    this.prNumber = props.prNumber;

    // Merge API config with defaults
    const apiConfig = { ...DEFAULT_API_CONFIG, ...props.apiConfig };

    // Set up infrastructure for Lambda, including role and log group
    const { lambdaRole, logGroup } = this.createLambdaInfrastructure();
    this.lambdaFunction = this.createLambdaFunction(lambdaRole, logGroup, props.lambdaConfig);

    // Create API Gateway with integrated Lambda function
    this.api = this.createApiGateway(apiConfig);

    // Configure routes and permissions for API Gateway
    this.configureApiGateway();

    // Define stack outputs for easy access to function ARN and API endpoint
    this.createStackOutputs();
  }

  /**
   * Creates infrastructure components for the Lambda function, including IAM role and CloudWatch Log Group.
   * @returns The IAM role and log group configured for Lambda.
   */
  private createLambdaInfrastructure() {
    // CloudWatch Log Group for Lambda logs with consistent naming
    const logGroup = new logs.LogGroup(this, 'MaintenanceFunctionLogGroup', {
      logGroupName: `/aws/lambda/${getResourceName(this.appName, this.stage, 'maintenanceFunctionLogGroup', this.prNumber)}`,
      retention: logs.RetentionDays.INFINITE,
    });

    // IAM role for Lambda, allowing access to necessary AWS resources
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

  /**
   * Creates the IAM policy for the Lambda function, granting permissions to write to CloudWatch Logs.
   * @returns A policy document with permissions for log access.
   */
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

  /**
   * Creates and configures the Lambda function with the specified settings.
   * @param role - The IAM role to associate with the Lambda function.
   * @param logGroup - CloudWatch log group for the Lambda function's logs.
   * @param config - Configuration properties for the Lambda function.
   * @returns The Lambda function instance.
   */
  private createLambdaFunction(
    role: iam.Role,
    logGroup: logs.LogGroup,
    config: LambdaConfig,
  ): lambda.Function {
    const functionName = getResourceName(this.appName, this.stage, 'maintenanceFunction', this.prNumber);

    return new lambda.Function(this, 'MaintenanceFunctionLambdaFunction', {
      functionName,
      description: `Maintenance API Lambda function for ${this.stage} stage`,
      runtime: config.runtime,
      handler: config.handler ?? 'maintenance_lambda.handler',
      code: lambda.Code.fromAsset(config.codePath ?? '../solution/backend/'),
      memorySize: config.memorySize,
      timeout: cdk.Duration.seconds(config.timeout),
      role,
      environment: {
        STAGE: this.stage,
        APP_NAME: this.appName,
      },
    });
  }

  /**
   * Creates and configures an API Gateway REST API to route requests to the Lambda function.
   * @param config - API Gateway configuration properties.
   * @returns The API Gateway instance.
   */
  private createApiGateway(config: ApiGatewayConfig): apigateway.RestApi {
    const apiName = getResourceName(this.appName, this.stage, 'apiGateway', this.prNumber);

    const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
      restApiName: apiName,
      description: `API Gateway for ${this.appName} ${this.stage}`,
      binaryMediaTypes: config.binaryMediaTypes,
      endpointConfiguration: {
        types: [config.endpointType!],
      },
      deployOptions: {
        stageName: this.stage,
        loggingLevel: config.loggingLevel,
      },
    });

    // API Gateway log group for access logs, using consistent naming
    new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: `/aws/api-gateway/${getResourceName(this.appName, this.stage, 'apiGatewayLogGroup', this.prNumber)}`,
    });

    return api;
  }

  /**
   * Configures routes in the API Gateway to handle requests and pass them to the Lambda function.
   */
  private configureApiGateway() {
    const integration = new apigateway.LambdaIntegration(this.lambdaFunction, { proxy: true });

    // Root and proxy resources setup for handling all paths and methods
    this.api.root.addMethod('ANY', integration, { apiKeyRequired: false, methodResponses: [{ statusCode: '200' }] });
    const proxyResource = this.api.root.addResource('{proxy+}');
    proxyResource.addMethod('ANY', integration, { apiKeyRequired: false, methodResponses: [{ statusCode: '200' }] });
  }

  /**
   * Creates CloudFormation outputs for the stack, providing easy access to the Lambda ARN and API endpoint.
   */
  private createStackOutputs() {
    const outputs: Record<string, cdk.CfnOutputProps> = {
      MaintenanceFunctionLambdaFunctionQualifiedArn: {
        value: this.lambdaFunction.functionArn,
        description: 'Current Lambda function version',
        exportName: getResourceName(this.appName, this.stage, 'MaintenanceFunctionLambdaFunctionQualifiedArn', this.prNumber),
      },
      ServiceEndpoint: {
        value: `https://${this.api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${this.stage}`,
        description: 'URL of the service endpoint',
        exportName: getResourceName(this.appName, this.stage, 'ServiceEndpoint', this.prNumber),
      },
    };

    // Define CloudFormation outputs
    Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
  }
}



// import * as cdk from 'aws-cdk-lib';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as apigateway from 'aws-cdk-lib/aws-apigateway';
// import * as iam from 'aws-cdk-lib/aws-iam';
// import * as logs from 'aws-cdk-lib/aws-logs';
// import { Construct } from 'constructs';
// import { BaseStack } from './base-stack';
// import { Environment, StackUtils } from '../../config/types/config-types';

// /**
//  * Props interface for the MaintenanceStack.
//  * Extends the basic CDK stack props with additional
//  * properties needed for our deployment patterns.
//  */
// export interface MaintenanceStackProps extends cdk.StackProps {
//   /** Deployment environment (dev, val, prod) */
//   stage: Environment;
//   /** PR number for experimental deployments */
//   prNumber?: string;
// }

// /**
//  * MaintenanceStack implements a simple API endpoint that can be used
//  * for maintenance mode or health checks. This implementation mirrors
//  * the configuration from serverless.yml while using CDK constructs.
//  * 
//  * Features:
//  * - Python Lambda function with basic request handling
//  * - API Gateway with proxy integration
//  * - IAM role with proper permissions and boundary
//  * - CloudWatch logs configuration
//  * - Support for experimental (PR-based) deployments
//  * 
//  * @example
//  * ```typescript
//  * new MaintenanceStack(app, 'maintenance-stack', {
//  *   stage: 'dev',
//  *   prNumber: '123', // Optional, for experimental deployments
//  * });
//  * ```
//  */
// export class MaintenanceStack extends BaseStack {
//   /** Lambda function that handles the maintenance endpoint */
//   private lambdaFunction?: lambda.Function;
//   /** API Gateway that exposes the Lambda function */
//   private api?: apigateway.RestApi;

//   constructor(scope: Construct, id: string, props: MaintenanceStackProps) {
//     super(scope, id, {
//       name: 'maintenance',
//       stage: props.stage,
//       prNumber: props.prNumber,
//       isExperimental: StackUtils.isExperimentalDeployment(props.prNumber),
//     }, props);

//     this.createResources();
//     this.addOutputs();
//   }

//   /**
//    * Creates all resources for the maintenance stack.
//    * This includes the Lambda function and API Gateway.
//    * @protected
//    */
//   protected createResources(): void {
//     this.createLambdaFunction();
//     this.createApiGateway();
//   }

//   /**
//    * Creates the Lambda function and its associated role.
//    * The function is configured with basic Python runtime
//    * and proper permissions for logging and execution.
//    * @private
//    */
//   private createLambdaFunction(): void {
//     // Create IAM role for Lambda function
//     const role = new iam.Role(this, 'LambdaRole', {
//       roleName: this.getResourceName('role', 'maintenance'),
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       // Fetch IAM path from SSM parameter store
//       path: this.parameterStore.getParameter('BASE', 'IAM_PATH'),
//       // Fetch and apply permissions boundary from SSM
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'PermissionsBoundary',
//         this.parameterStore.getParameter('BASE', 'PERMISSIONS_BOUNDARY')
//       ),
//       // Apply required managed policies
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName(
//           'service-role/AWSLambdaVPCAccessExecutionRole'
//         ),
//       ],
//     });

//     // Add CloudWatch Logs permissions
//     role.addToPolicy(
//       new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: [
//           'logs:CreateLogGroup',
//           'logs:CreateLogStream',
//           'logs:PutLogEvents',
//         ],
//         resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
//       })
//     );

//     // Create Lambda function
//     this.lambdaFunction = new lambda.Function(this, 'MaintenanceFunction', {
//       functionName: this.getResourceName('function', 'maintenance'),
//       runtime: lambda.Runtime.PYTHON_3_12,
//       handler: 'maintenance_lambda.handler',
//       code: lambda.Code.fromAsset('../lambda/maintenance'),
//       memorySize: 128,
//       timeout: cdk.Duration.seconds(30),
//       environment: {
//         STAGE: this.stackPrefix,
//       },
//       role,
//       tracing: lambda.Tracing.ACTIVE,
//     });

//     // Create CloudWatch log group with retention
//     new logs.LogGroup(this, 'LambdaLogGroup', {
//       logGroupName: `/aws/lambda/${this.lambdaFunction.functionName}`,
//       retention: logs.RetentionDays.ONE_MONTH,
//       // Use stack's removal policy (DESTROY for experimental, RETAIN for regular deployments)
//       removalPolicy: this.removalPolicy,
//     });
//   }

//   /**
//    * Creates the API Gateway with proxy integration to the Lambda function.
//    * Configures binary media types and logging as specified in serverless.yml.
//    * @private
//    */
//   private createApiGateway(): void {
//     this.api = new apigateway.RestApi(this, 'MaintenanceApi', {
//       restApiName: this.getResourceName('api', 'maintenance'),
//       description: 'Maintenance API Service',
//       deployOptions: {
//         stageName: this.config.stage,
//         tracingEnabled: true,
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         metricsEnabled: true,
//       },
//       // Match binary media types from serverless.yml
//       binaryMediaTypes: [
//         'multipart/form-data',
//         'application/pdf',
//       ],
//     });

//     // Add proxy integration to handle all methods and paths
//     this.api.root.addProxy({
//       defaultIntegration: new apigateway.LambdaIntegration(this.lambdaFunction!),
//       anyMethod: true,
//     });
//   }

//   /**
//    * Adds CloudFormation outputs for the stack resources.
//    * These outputs can be used by other stacks or for reference.
//    * @private
//    */
//   private addOutputs(): void {
//     // Output Lambda ARN
//     if (this.lambdaFunction) {
//       new cdk.CfnOutput(this, 'LambdaArn', {
//         value: this.lambdaFunction.functionArn,
//         description: 'Maintenance Lambda Function ARN',
//         exportName: `${this.stackPrefix}-maintenance-lambda-arn`,
//       });
//     }

//     // Output API Gateway URL
//     if (this.api) {
//       new cdk.CfnOutput(this, 'ApiUrl', {
//         value: this.api.url,
//         description: 'Maintenance API Gateway URL',
//         exportName: `${this.stackPrefix}-maintenance-api-url`,
//       });
//     }
//   }
// }
