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
 * Properties for the MaintenanceApiStack
 */
export interface MaintenanceApiStackProps extends cdk.StackProps {
  lambdaConfig: LambdaConfig;
  apiConfig?: ApiGatewayConfig;
}

const DEFAULT_API_CONFIG: ApiGatewayConfig = {
  binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
  endpointType: apigateway.EndpointType.EDGE,
  loggingLevel: apigateway.MethodLoggingLevel.INFO,
};

export class MaintenanceApiStack extends cdk.Stack {
  public readonly lambdaFunction: lambda.Function;
  public readonly api: apigateway.RestApi;
  private readonly stageConfig: StageConfig;

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

  private createLambdaInfrastructure() {
    // Lambda CloudWatch Log Group
    const logGroup = new logs.LogGroup(this, 'MaintenanceFunctionLogGroup', {
      logGroupName: `/aws/lambda/maintenance-api-${this.stageConfig.environment}-maintenanceFunction`,
    });

    // Lambda IAM Role
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
    const fn = new lambda.Function(this, 'MaintenanceFunctionLambda', {
      functionName: `maintenance-api-${this.stageConfig.environment}-maintenanceFunction`,
      runtime: config.runtime,
      handler: 'maintenance_lambda.handler',
      code: lambda.Code.fromAsset(config.codePath ?? '../solution/backend/'),
      memorySize: config.memorySize,
      timeout: cdk.Duration.seconds(config.timeout),
      role,
    });

    // Create version (matches template)
    new lambda.Version(this, 'MaintenanceFunctionVersion', {
      lambda: fn,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    return fn;
  }

  private createApiGateway(config: ApiGatewayConfig): apigateway.RestApi {
    const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
      restApiName: `${this.stageConfig.environment}-maintenance-api`,
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
      logGroupName: `/aws/api-gateway/maintenance-api-${this.stageConfig.environment}`,
    });

    return api;
  }

  private configureApiGateway() {
    const integration = new apigateway.LambdaIntegration(this.lambdaFunction, { proxy: true });

    // Lambda permission for API Gateway
    new lambda.CfnPermission(this, 'MaintenanceFunctionLambdaPermissionApiGateway', {
      action: 'lambda:InvokeFunction',
      functionName: this.lambdaFunction.functionArn,
      principal: 'apigateway.amazonaws.com',
      sourceArn: `arn:${this.partition}:execute-api:${this.region}:${this.account}:${this.api.restApiId}/*/*`,
    });
    
    this.api.root.addMethod('ANY', integration, { 
      apiKeyRequired: false, 
      methodResponses: [] 
    });
    
    const proxyResource = this.api.root.addResource('{proxy+}');
    proxyResource.addMethod('ANY', integration, { 
      apiKeyRequired: false, 
      methodResponses: [] 
    });
  }

  private createStackOutputs() {
    const outputs: Record<string, cdk.CfnOutputProps> = {
      MaintenanceFunctionLambdaFunctionQualifiedArn: {
        value: this.lambdaFunction.currentVersion.functionArn,
        description: 'Current Lambda function version',
        exportName: `sls-maintenance-api-${this.stageConfig.environment}-MaintenanceFunctionLambdaFunctionQualifiedArn`,
      },
      ServiceEndpoint: {
        value: `https://${this.api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${this.stageConfig.environment}`,
        description: 'URL of the service endpoint',
        exportName: `sls-maintenance-api-${this.stageConfig.environment}-ServiceEndpoint`,
      },
    };

    Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
  }
}