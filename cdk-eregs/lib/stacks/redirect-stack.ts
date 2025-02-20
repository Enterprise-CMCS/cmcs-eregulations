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
      retention: logs.RetentionDays.ONE_MONTH,
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

