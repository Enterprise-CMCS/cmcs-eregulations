import * as cdk from 'aws-cdk-lib';
import {
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda,
    aws_apigateway as apigateway,
    aws_ssm as ssm,
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
    constructor(scope: Construct, id: string, props: RedirectApiStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        const apiConfig = { ...DEFAULT_API_CONFIG, ...props.apiConfig };
        const customUrl = stageConfig.stageName === "prod" ? ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url') : "";

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'RedirectFunctionLogGroup', {
            logGroupName: stageConfig.aws.lambda('redirect-function'),
            retention: logs.RetentionDays.INFINITE,
        });

        // ================================
        // LAMBDA ROLE
        // ================================
        const lambdaPolicy = new iam.PolicyDocument({
            statements: [
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
                    resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
                }),
            ],
        });

        const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
            ],
            inlinePolicies: {
                LambdaPolicy: lambdaPolicy,
            },
        });

        // ================================
        // LAMBDA FUNCTION
        // ================================
        const lambdaFunction = new lambda.Function(this, 'RedirectFunctionLambdaFunction', {
            functionName: stageConfig.getResourceName('redirect-function'),
            description: `Redirect API Lambda function for ${stageConfig.environment} stage`,
            runtime: props.lambdaConfig.runtime,
            handler: props.lambdaConfig.handler ?? 'redirect_lambda.handler',
            code: lambda.Code.fromAsset(props.lambdaConfig.codePath ?? '../solution/backend/'),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            role: lambdaRole,
            environment: {
                STAGE: stageConfig.environment,
                APP_NAME: StageConfig.projectName,
                CUSTOM_URL: customUrl,
            },
        });

        // ================================
        // API GATEWAY
        // ================================
        const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
            restApiName: stageConfig.getResourceName('api-gateway'),
            description: `API Gateway for ${StageConfig.projectName} ${stageConfig.environment}`,
            binaryMediaTypes: apiConfig.binaryMediaTypes,
            endpointConfiguration: {
                types: [apiConfig.endpointType!],
            },
            deployOptions: {
                stageName: stageConfig.environment,
                loggingLevel: apiConfig.loggingLevel,
            },
        });

        // API Gateway Log Group
        new logs.LogGroup(this, 'ApiGatewayLogGroup', {
            logGroupName: stageConfig.aws.apiGateway('api-gateway'),
        });

        const integration = new apigateway.LambdaIntegration(lambdaFunction, { proxy: true });
    
        api.root.addMethod('ANY', integration, { 
            apiKeyRequired: false, 
            methodResponses: [{ statusCode: '200' }] 
        });
    
        const proxyResource = api.root.addResource('{proxy+}');
        proxyResource.addMethod('ANY', integration, { 
            apiKeyRequired: false, 
            methodResponses: [{ statusCode: '200' }] 
        });
    
        // ================================
        // STACK OUTPUTS
        // ================================
        const outputs: Record<string, cdk.CfnOutputProps> = {
            RedirectFunctionLambdaFunctionQualifiedArn: {
                value: lambdaFunction.functionArn,
                description: 'Current Lambda function version',
                exportName: stageConfig.getResourceName('redirect-function-arn'),
            },
            ServiceEndpoint: {
                value: `https://${api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${stageConfig.environment}`,
                description: 'URL of the service endpoint',
                exportName: stageConfig.getResourceName('service-endpoint'),
            },
        };

        Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
    }
}
