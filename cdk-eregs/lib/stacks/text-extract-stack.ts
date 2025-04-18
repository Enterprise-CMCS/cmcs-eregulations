import * as cdk from 'aws-cdk-lib';
import {
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda,
    aws_sqs as sqs,
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
    /** Name of secret for authentication **/
    secretName: string;
}

/**
 * Properties interface for TextExtractorStack.
 * Extends standard CDK stack properties with custom configuration settings.
 */
export interface TextExtractorStackProps extends cdk.StackProps {
    /** Lambda function configuration settings */
    lambdaConfig: LambdaConfig;
    /** Environment-specific configuration settings */
    environmentConfig: EnvironmentConfig;
}

/**
 * CDK Stack implementation for Text Extractor service.
 * 
 * This stack creates a serverless text extraction service with the following components:
 * - Docker-based Lambda function for text extraction using AWS managed VPC
 * - SQS Queue with Dead Letter Queue for reliable message processing
 * - IAM roles and policies for secure access
 * - CloudWatch Log Groups for monitoring
 * - Event Source Mapping for queue integration
 */
export class TextExtractorStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: TextExtractorStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        // ================================
        // SQS QUEUES
        // ================================
        const deadLetterQueue = new sqs.Queue(this, 'DeadLetterQueue', {
            queueName: stageConfig.getResourceName('text-extractor-dl-queue'),
        });

        const queue = new sqs.Queue(this, 'TextExtractorQueue', {
            queueName: stageConfig.getResourceName('text-extractor-queue'),
            visibilityTimeout: cdk.Duration.seconds(900),
            retentionPeriod: cdk.Duration.days(4),
            deadLetterQueue: {
                maxReceiveCount: 5,
                queue: deadLetterQueue,
            },
        });

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'TextExtractorLogGroup', {
            logGroupName: stageConfig.aws.lambda('text-extractor'),
            retention: logs.RetentionDays.INFINITE,
        });

        // ================================
        // LAMBDA ROLE
        // ================================
        const sqsPolicy = new iam.PolicyDocument({
            statements: [
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        'sqs:ReceiveMessage',
                        'sqs:DeleteMessage',
                        'sqs:GetQueueAttributes'
                    ],
                    resources: [queue.queueArn],
                }),
            ],
        });

        const textDetectionPolicy = new iam.PolicyDocument({
            statements: [
                new iam.PolicyStatement({
                    sid: 'DetectDocumentText',
                    effect: iam.Effect.ALLOW,
                    actions: ['textract:DetectDocumentText'],
                    resources: ['*'],
                }),
            ],
        });

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
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        's3:GetObject',
                    ],
                    resources: [
                        `arn:aws:s3:::cms-eregs-${stageConfig.stageName}-file-repo-eregs*`,
                    ],
                }),
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        'secretsmanager:GetSecretValue',
                    ],
                    resources: [
                        `arn:aws:secretsmanager:${this.region}:${this.account}:secret:${props.environmentConfig.secretName}*`,
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
                iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
            ],
            inlinePolicies: {
                QueuePolicy: sqsPolicy,
                TextDetectionPolicy: textDetectionPolicy,
                LambdaPolicy: lambdaPolicy,
            },
        });

        // ================================
        // LAMBDA FUNCTION
        // ================================
        const lambdaFunction = new lambda.DockerImageFunction(this, 'TextExtractorFunction', {
            functionName: stageConfig.getResourceName('text-extractor'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'text-extractor/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            reservedConcurrentExecutions: props.lambdaConfig.reservedConcurrentExecutions,
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                SECRET_NAME: props.environmentConfig.secretName,
            },
            role: lambdaRole,
        });

        new lambda.EventSourceMapping(this, 'TextExtractorEventSourceMapping', {
            target: lambdaFunction,
            batchSize: 1,
            eventSourceArn: queue.queueArn,
            enabled: true,
        });

        // ================================
        // STACK OUTPUTS
        // ================================
        const outputs: Record<string, cdk.CfnOutputProps> = {
            TextExtractorLambdaFunctionQualifiedArn: {
                value: lambdaFunction.functionArn,
                description: 'Current Lambda function version',
                exportName: stageConfig.getResourceName('text-extractor-lambda-arn'),
            },
            TextExtractorQueueUrl: {
                value: queue.queueUrl,
                exportName: stageConfig.getResourceName('text-extractor-queue-url'),
            },
            TextExtractorQueueArn: {
                value: queue.queueArn,
                exportName: stageConfig.getResourceName('text-extractor-queue-arn'),
            }
        };

        Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
    }
}

