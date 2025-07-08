import * as cdk from 'aws-cdk-lib';
import {
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda,
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
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
            queueName: stageConfig.getResourceName('text-extractor-dl-queue.fifo'),
            fifo: true,
        });

        const queue = new sqs.Queue(this, 'TextExtractorQueue', {
            queueName: stageConfig.getResourceName('text-extractor-queue.fifo'),
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
        // S3 BUCKET FOR TEMP PDF STORAGE
        // ================================
        const pdfBucket = new s3.Bucket(this, 'TextractPdfBucket', {
            bucketName: stageConfig.getResourceName('textract-pdf-bucket'),
            encryption: s3.BucketEncryption.S3_MANAGED,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            enforceSSL: true,
            autoDeleteObjects: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            cors: [
                {
                    allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowedOrigins: ['*'],
                    allowedHeaders: ['*'],
                    maxAge: 3000,
                },
            ],
        });

        // Allow Textract to access the S3 bucket
        pdfBucket.addToResourcePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            principals: [new iam.ServicePrincipal('textract.amazonaws.com')],
            actions: ['s3:GetObject'],
            resources: [`${pdfBucket.bucketArn}/*`],
        }));

        // ================================
        // S3 BUCKET FOR TEXTRACT RESULTS
        // ================================
        const textractResultsBucket = new s3.Bucket(this, 'TextractResultsBucket', {
            bucketName: stageConfig.getResourceName('textract-results-bucket'),
            encryption: s3.BucketEncryption.S3_MANAGED,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            enforceSSL: true,
            autoDeleteObjects: true,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
            cors: [
                {
                    allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowedOrigins: ['*'],
                    allowedHeaders: ['*'],
                    maxAge: 3000,
                },
            ],
        });

        // Allow Textract to write results to the S3 bucket
        textractResultsBucket.addToResourcePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            principals: [new iam.ServicePrincipal('textract.amazonaws.com')],
            actions: ['s3:PutObject'],
            resources: [`${textractResultsBucket.bucketArn}/*`],
        }));

        // ================================
        // EVENTBRIDGE RULE FOR TEXTRACT RESULTS BUCKET
        // ================================
        new events.Rule(this, 'TextractResultsS3EventRule', {
            ruleName: stageConfig.getResourceName('textract-results-s3-event-rule'),
            eventPattern: {
                source: ['aws.s3'],
                detailType: ['Object Created'],
                resources: [textractResultsBucket.bucketArn],
                detail: {
                    bucket: {
                        name: [textractResultsBucket.bucketName],
                    },
                },
            },
            targets: [new targets.SqsQueue(queue, {messageGroupId: 'TextractResults'})],
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
                    actions: [
                        'textract:DetectDocumentText',
                        'textract:StartDocumentTextDetection',
                        'textract:GetDocumentTextDetection',
                    ],
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
                // Allow Lambda read/write access to the PDF bucket
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        's3:PutObject',
                        's3:GetObject',
                        's3:DeleteObject',
                    ],
                    resources: [
                        `arn:aws:s3:::${pdfBucket.bucketName}/*`,
                    ],
                }),
                // Allow Lambda read/delete access to the Textract results bucket
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        's3:GetObject',
                        's3:DeleteObject',
                    ],
                    resources: [
                        `${textractResultsBucket.bucketArn}/*`,
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
            },
        };

        Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
    }
}
