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
    /**
     * Creates a new instance of MaintenanceApiStack.
     * @param scope - The scope in which to define this construct
     * @param id - The scoped construct ID
     * @param props - Configuration properties for the stack
     * @param stageConfig - Stage configuration for environment-aware resource creation
     */
    constructor(scope: Construct, id: string, props: MaintenanceApiStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        const apiConfig = { ...DEFAULT_API_CONFIG, ...props.apiConfig };

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'MaintenanceFunctionLogGroup', {
            logGroupName: stageConfig.aws.lambda('maintenance-function'),
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
                LambdaPolicy: lambdaPolicy,
            },
        });

        // ================================
        // LAMBDA FUNCTION
        // ================================
        const lambdaFunction = new lambda.Function(this, 'MaintenanceFunctionLambda', {
            functionName: stageConfig.getResourceName('maintenance-function'),
            description: `Maintenance API Lambda function for ${stageConfig.environment} stage`,
            runtime: props.lambdaConfig.runtime,
            handler: props.lambdaConfig.handler ?? 'maintenance_lambda.handler',
            code: lambda.Code.fromAsset(props.lambdaConfig.codePath ?? '../solution/backend/'),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            role: lambdaRole,
            environment: {
                STAGE: stageConfig.environment,
                APP_NAME: StageConfig.projectName,
            },
        });

        // ================================
        // API GATEWAY
        // ================================
        const api = new apigateway.RestApi(this, 'ApiGatewayRestApi', {
            restApiName: stageConfig.getResourceName('maintenance-api'),
            description: `Maintenance API Gateway for ${StageConfig.projectName} ${stageConfig.environment}`,
            binaryMediaTypes: apiConfig.binaryMediaTypes,
            endpointConfiguration: {
                types: [apiConfig.endpointType!],
            },
            deployOptions: {
                stageName: stageConfig.environment,
                loggingLevel: apiConfig.loggingLevel,
            },
        });

        // Create API Gateway Log Group
        new logs.LogGroup(this, 'ApiGatewayLogGroup', {
            logGroupName: stageConfig.aws.apiGateway('maintenance-api'),
        });

        const integration = new apigateway.LambdaIntegration(lambdaFunction, { proxy: true });

        // Configure root path
        api.root.addMethod('ANY', integration, { 
            apiKeyRequired: false, 
            methodResponses: [{ statusCode: '200' }] 
        });
    
        // Configure proxy path
        const proxyResource = api.root.addResource('{proxy+}');
        proxyResource.addMethod('ANY', integration, { 
            apiKeyRequired: false, 
            methodResponses: [{ statusCode: '200' }] 
        });

        // ================================
        // STACK OUTPUTS
        // ================================
        const outputs: Record<string, cdk.CfnOutputProps> = {
            MaintenanceFunctionLambdaFunctionQualifiedArn: {
                value: lambdaFunction.functionArn,
                description: 'Current Lambda function version',
                exportName: stageConfig.getResourceName('maintenance-function-arn'),
            },
            ServiceEndpoint: {
                value: `https://${api.restApiId}.execute-api.${this.region}.${cdk.Aws.URL_SUFFIX}/${stageConfig.environment}`,
                description: 'URL of the service endpoint',
                exportName: stageConfig.getResourceName('maintenance-service-endpoint'),
            },
        };

        Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
    }
}
