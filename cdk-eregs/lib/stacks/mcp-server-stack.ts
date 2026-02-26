import * as cdk from 'aws-cdk-lib';
import {
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda,
    aws_sqs as sqs,
    aws_s3 as s3,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import * as path from 'path';

/**
 * Configuration interface for Lambda function settings.
 * Defines required and optional parameters for Lambda function configuration.
 */
interface LambdaConfig {
    /** Memory allocation in MB for the Lambda function */
    memorySize: number;
    /** Function timeout in seconds */
    timeout: number;
    /** Optional limit on concurrent executions */
    reservedConcurrentExecutions?: number;
}

/**
 * Configuration interface for environment-specific settings.
 * Contains all the external configuration values needed for the stack.
 */
interface EnvironmentConfig {
    /** Log level for the Lambda function (e.g., DEBUG, INFO) */
    logLevel: string;
}

/**
 * Properties interface for McpServerStack.
 * Extends standard CDK stack properties with custom configuration settings.
 */
export interface McpServerStackProps extends cdk.StackProps {
    /** Lambda function configuration settings */
    lambdaConfig: LambdaConfig;
    /** Environment-specific configuration settings */
    environmentConfig: EnvironmentConfig;
}

/**
 * CDK Stack implementation for MCP Server service.
 *
 * This stack creates a serverless MCP Server service with the following components:
 * - Docker-based Lambda function for MCP Server using AWS managed VPC
 * - IAM roles and policies for secure access
 * - CloudWatch Log Groups for monitoring
 */
export class McpServerStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: McpServerStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'McpServerLogGroup', {
            logGroupName: stageConfig.aws.lambda('mcp-server'),
            retention: logs.RetentionDays.INFINITE,
        });

        // ================================
        // LAMBDA ROLE
        // ================================

        const lambdaPolicy = new iam.PolicyDocument({
            statements: [
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        'logs:CreateLogGroup',
                        'logs:CreateLogStream',
                        'logs:PutLogEvents'
                    ],
                    resources: [
                        `arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`,
                    ],
                }),
            ],
        });

        const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
            path: stageConfig.iamPath,
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
                this,
                'PermissionsBoundary',
                stageConfig.permissionsBoundaryArn
            ),
            managedPolicies: [
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
            ],
            inlinePolicies: {
                LambdaPolicy: lambdaPolicy,
            },
        });

        // ================================
        // LAMBDA FUNCTION
        // ================================
        const siteEndpoint = cdk.Fn.importValue(stageConfig.getResourceName('api-endpoint'))

        const lambdaFunction = new lambda.DockerImageFunction(this, 'McpServerFunction', {
            functionName: stageConfig.getResourceName('mcp-server'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'mcp-server/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            reservedConcurrentExecutions: props.lambdaConfig.reservedConcurrentExecutions,
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                EREGS_API_URL_V3: `${siteEndpoint}v3/`,
            },
            role: lambdaRole,
        });

        // ================================
        // STACK OUTPUTS
        // ================================
        const outputs: Record<string, cdk.CfnOutputProps> = {
            McpServerLambdaFunctionQualifiedArn: {
                value: lambdaFunction.functionArn,
                description: 'Current Lambda function version',
                exportName: stageConfig.getResourceName('mcp-server-lambda-arn'),
            },
        };

        Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
    }
}
