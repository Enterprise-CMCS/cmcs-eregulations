// lib/stacks/maintenance-api-stack.ts
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
 * Properties for the MaintenanceApiStack, including Lambda and API Gateway configurations.
 */
export interface MaintenanceApiStackProps extends cdk.StackProps {
  lambdaConfig: LambdaConfig;
  apiConfig?: ApiGatewayConfig;
}

/**
 * Default API Gateway configuration for the maintenance API
 */
const DEFAULT_API_CONFIG: ApiGatewayConfig = {
  binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
  endpointType: apigateway.EndpointType.EDGE,
  loggingLevel: apigateway.MethodLoggingLevel.INFO,
};

/**
 * CDK Stack for creating a Maintenance API with Lambda backend.
 * This stack creates:
 * - Lambda function with proper IAM roles and permissions
 * - API Gateway with proxy integration to Lambda
 * - CloudWatch log groups for both Lambda and API Gateway
 *
 * @example
 * ```typescript
 * const app = new cdk.App();
 * const stageConfig = await StageConfig.create('dev', 'eph-123');
 *
 * new MaintenanceApiStack(app, stageConfig.getResourceName('maintenance-api'), {
 *   lambdaConfig: {
 *     runtime: lambda.Runtime.PYTHON_3_12,
 *     memorySize: 1024,
 *     timeout: 30,
 *   }
 * }, stageConfig);
 * ```
 */
export class MaintenanceApiStack extends cdk.Stack {
  public readonly lambdaFunction: lambda.Function;
  public readonly api: apigateway.RestApi;
  private readonly stageConfig: StageConfig;

  /**
   * Creates a new instance of MaintenanceApiStack.
   * @param scope - The scope in which to define this construct
   * @param id - The scoped construct ID
   * @param props - Configuration properties for the stack
   * @param stageConfig - Stage configuration for environment-aware resource creation
   */
  constructor(
    scope: Construct,
    id: string,
    props: MaintenanceApiStackProps,
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

  /**
   * Creates the Lambda function's infrastructure components including:
   * - CloudWatch Log Group
   * - IAM Role with appropriate permissions
   *
   * @returns Object containing the created role and log group
   */
  private createLambdaInfrastructure() {
    // Create CloudWatch Log Group with environment-aware naming
    const logGroup = new logs.LogGroup(this, 'MaintenanceFunctionLogGroup', {
      logGroupName: this.stageConfig.aws.lambda('maintenance-function'),
      retention: logs.RetentionDays.ONE_MONTH,
    });

    // Create IAM Role with required permissions
    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      path: '/delegatedadmin/developer/',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy/cms-cloud-admin/developer-boundary-policy`
      ),
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
   * Creates the IAM policy document for Lambda CloudWatch Logs permissions
   * @returns PolicyDocument with CloudWatch Logs write permissions
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
   * Creates and configures the Lambda function
   * @param role - IAM role for the Lambda function
   * @param logGroup - CloudWatch Log Group for Lambda logs
   * @param config - Lambda function configuration
   * @returns Configured Lambda function
   */
  private createLambdaFunction(
    role: iam.Role,
    logGroup: logs.LogGroup,
    config: LambdaConfig,
  ): lambda.Function {
    return new lambda.Function(this, 'MaintenanceFunctionLambda', {
      functionName: this.stageConfig.getResourceName('maintenance-function'),
      description: `Maintenance API Lambda function for ${this.stageConfig.environment} stage`,
      runtime: config.runtime,
      handler: config.handler ?? 'maintenance_lambda.handler',
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

  /**
   * Creates and configures the API Gateway
   * @param config - API Gateway configuration
   * @returns Configured REST API
   */
  private createApiGateway(config: ApiGatewayConfig): apigateway.RestApi {
    const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
      restApiName: this.stageConfig.getResourceName('maintenance-api'),
      description: `Maintenance API Gateway for ${StageConfig.projectName} ${this.stageConfig.environment}`,
      binaryMediaTypes: config.binaryMediaTypes,
      endpointConfiguration: {
        types: [config.endpointType!],
      },
      deployOptions: {
        stageName: this.stageConfig.environment,
        loggingLevel: config.loggingLevel,
      },
    });

    // Create API Gateway Log Group
    new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: this.stageConfig.aws.apiGateway('maintenance-api'),
    });

    return api;
  }

  /**
   * Configures API Gateway routes and integrations
   * Sets up:
   * - Lambda proxy integration
   * - ANY method on root path
   * - ANY method on proxy resource (/{proxy+})
   */
  private configureApiGateway() {
    const integration = new apigateway.LambdaIntegration(this.lambdaFunction, { proxy: true });

    // Configure root path
    this.api.root.addMethod('ANY', integration, {
      apiKeyRequired: false,
      methodResponses: [{ statusCode: '200' }]
    });

    // Configure proxy path
    const proxyResource = this.api.root.addResource('{proxy+}');
    proxyResource.addMethod('ANY', integration, {
      apiKeyRequired: false,
      methodResponses: [{ statusCode: '200' }]
    });
  }

  /**
   * Creates CloudFormation outputs for the stack
   * Exports:
   * - Lambda function ARN
   * - API Gateway endpoint URL
   */
  private createStackOutputs() {
    const outputs: Record<string, cdk.CfnOutputProps> = {
      MaintenanceFunctionLambdaFunctionQualifiedArn: {
        value: this.lambdaFunction.functionArn,
        description: 'Current Lambda function version',
        exportName: this.stageConfig.getResourceName('maintenance-function-arn'),
      },
      ServiceEndpoint: {
        value: `https://${this.api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${this.stageConfig.environment}`,
        description: 'URL of the service endpoint',
        exportName: this.stageConfig.getResourceName('maintenance-service-endpoint'),
      },
    };

    Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
  }
}