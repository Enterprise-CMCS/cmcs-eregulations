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
 * Properties interface for EmbeddingGeneratorStack.
 * Extends standard CDK stack properties with custom configuration settings.
 */
export interface EmbeddingGeneratorStackProps extends cdk.StackProps {
    /** Lambda function configuration settings */
    lambdaConfig: LambdaConfig;
    /** Environment-specific configuration settings */
    environmentConfig: EnvironmentConfig;
}

/**
 * CDK Stack implementation for Embedding Generator service.
 *
 * This stack creates a serverless embedding generation service with the following components:
 * - Docker-based Lambda function for embedding generation using AWS managed VPC
 * - SQS Queue with Dead Letter Queue for reliable message processing
 * - IAM roles and policies for secure access
 * - CloudWatch Log Groups for monitoring
 * - Event Source Mapping for queue integration
 */
export class EmbeddingGeneratorStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: EmbeddingGeneratorStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        // ================================
        // SQS QUEUES
        // ================================
        const deadLetterQueue = new sqs.Queue(this, 'DeadLetterQueue', {
            queueName: stageConfig.getResourceName('embedding-generator-dl-queue.fifo'),
            fifo: true,
        });

        const queue = new sqs.Queue(this, 'EmbeddingGeneratorQueue', {
            queueName: stageConfig.getResourceName('embedding-generator-queue.fifo'),
            fifo: true,
            visibilityTimeout: cdk.Duration.seconds(900),
            retentionPeriod: cdk.Duration.days(14),
            contentBasedDeduplication: true,
            deadLetterQueue: {
                maxReceiveCount: 5,
                queue: deadLetterQueue,
            },
        });

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'EmbeddingGeneratorLogGroup', {
            logGroupName: stageConfig.aws.lambda('embedding-generator'),
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
                        'sqs:SendMessage',
                        'sqs:ReceiveMessage',
                        'sqs:DeleteMessage',
                        'sqs:GetQueueAttributes'
                    ],
                    resources: [queue.queueArn],
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
                        'secretsmanager:GetSecretValue',
                    ],
                    resources: [
                        `arn:aws:secretsmanager:${this.region}:${this.account}:secret:${props.environmentConfig.secretName}*`,
                    ],
                }),
                // Allow function to use Bedrock (Titan Embeddings model V2)
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        'bedrock:InvokeModel',
                        'bedrock:BatchInvokeModel',
                        'bedrock:ListModels',
                    ],
                    resources: [
                        'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0',
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
                QueuePolicy: sqsPolicy,
                LambdaPolicy: lambdaPolicy,
            },
        });

        // ================================
        // LAMBDA FUNCTION
        // ================================
        const lambdaFunction = new lambda.DockerImageFunction(this, 'EmbeddingGeneratorFunction', {
            functionName: stageConfig.getResourceName('embedding-generator'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'embedding-generator/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            reservedConcurrentExecutions: props.lambdaConfig.reservedConcurrentExecutions,
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                SECRET_NAME: props.environmentConfig.secretName,
                EMBEDDING_GENERATOR_QUEUE_URL: queue.queueUrl,
            },
            role: lambdaRole,
        });

        new lambda.EventSourceMapping(this, 'EmbeddingGeneratorEventSourceMapping', {
            target: lambdaFunction,
            batchSize: 1,
            eventSourceArn: queue.queueArn,
            enabled: true,
        });

        // ================================
        // STACK OUTPUTS
        // ================================
        const outputs: Record<string, cdk.CfnOutputProps> = {
            EmbeddingGeneratorLambdaFunctionQualifiedArn: {
                value: lambdaFunction.functionArn,
                description: 'Current Lambda function version',
                exportName: stageConfig.getResourceName('embedding-generator-lambda-arn'),
            },
            EmbeddingGeneratorQueueUrl: {
                value: queue.queueUrl,
                exportName: stageConfig.getResourceName('embedding-generator-queue-url'),
            },
            EmbeddingGeneratorQueueArn: {
                value: queue.queueArn,
                exportName: stageConfig.getResourceName('embedding-generator-queue-arn'),
            },
        };

        Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
    }
}
