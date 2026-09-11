import * as cdk from 'aws-cdk-lib';
import {
    aws_lambda as lambda,
    aws_logs as logs,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_events as events,
    aws_events_targets as targets,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import * as path from 'path';

interface LambdaConfig {
    memorySize: number;
    timeout: number;
}

interface EnvironmentConfig {
    logLevel: string;
    authSecretName: string;
}

export interface EcfrParserStackProps extends cdk.StackProps {
    lambdaConfig: LambdaConfig;
    environmentConfig: EnvironmentConfig;
}

export class EcfrParserStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: EcfrParserStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        const siteEndpoint = cdk.Fn.importValue(stageConfig.getResourceName('api-endpoint'));

        const deadLetterQueue = new sqs.Queue(this, 'EcfrParserDeadLetterQueue', {
            queueName: stageConfig.getResourceName('ecfr-parser-dlq'),
            retentionPeriod: cdk.Duration.days(14),
        });

        const queue = new sqs.Queue(this, 'EcfrParserQueue', {
            queueName: stageConfig.getResourceName('ecfr-parser-queue'),
            visibilityTimeout: cdk.Duration.seconds(900),
            retentionPeriod: cdk.Duration.days(14),
            deadLetterQueue: {
                queue: deadLetterQueue,
                maxReceiveCount: 5,
            },
        });

        new logs.LogGroup(this, 'EcfrParserWorkerLogGroup', {
            logGroupName: stageConfig.aws.lambda('ecfr-parser-worker'),
            retention: logs.RetentionDays.INFINITE,
        });

        new logs.LogGroup(this, 'EcfrParserLauncherLogGroup', {
            logGroupName: stageConfig.aws.lambda('ecfr-parser-launcher'),
            retention: logs.RetentionDays.INFINITE,
        });

        const worker = new lambda.DockerImageFunction(this, 'EcfrParserWorkerFunction', {
            functionName: stageConfig.getResourceName('ecfr-parser-worker'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'parsers/ecfr-worker/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                EREGS_API_URL_V3: `${siteEndpoint}v3/`,
                ECFR_API_BASE_URL: 'https://www.ecfr.gov/api/versioner/v1/',
                EREGS_AUTH_SECRET_NAME: props.environmentConfig.authSecretName,
            },
        });

        const launcher = new lambda.DockerImageFunction(this, 'EcfrParserLauncherFunction', {
            functionName: stageConfig.getResourceName('ecfr-parser-launcher'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'parsers/ecfr-launcher/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                EREGS_API_URL_V3: `${siteEndpoint}v3/`,
                ECFR_API_BASE_URL: 'https://www.ecfr.gov/api/versioner/v1/',
                EREGS_AUTH_SECRET_NAME: props.environmentConfig.authSecretName,
                PARSER_QUEUE_URL: queue.queueUrl,
            },
        });

        const secretArn = `arn:aws:secretsmanager:${this.region}:${this.account}:secret:${props.environmentConfig.authSecretName}*`;
        const secretReadPolicy = new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: ['secretsmanager:GetSecretValue'],
            resources: [secretArn],
        });
        worker.addToRolePolicy(secretReadPolicy);
        launcher.addToRolePolicy(secretReadPolicy);

        queue.grantConsumeMessages(worker);
        queue.grantSendMessages(launcher);

        new lambda.EventSourceMapping(this, 'EcfrParserWorkerEventSource', {
            target: worker,
            batchSize: 1,
            eventSourceArn: queue.queueArn,
            enabled: true,
        });

        const rule = new events.Rule(this, 'EcfrParserLauncherSchedule', {
            schedule: events.Schedule.expression('cron(0 0 * * ? *)'),
            enabled: true,
        });
        rule.addTarget(new targets.LambdaFunction(launcher));

        const outputs: Record<string, cdk.CfnOutputProps> = {
            EcfrParserQueueArn: {
                value: queue.queueArn,
                exportName: stageConfig.getResourceName('ecfr-parser-queue-arn'),
            },
            EcfrParserQueueUrl: {
                value: queue.queueUrl,
                exportName: stageConfig.getResourceName('ecfr-parser-queue-url'),
            },
            EcfrParserDlqArn: {
                value: deadLetterQueue.queueArn,
                exportName: stageConfig.getResourceName('ecfr-parser-dlq-arn'),
            },
            EcfrParserWorkerLambdaArn: {
                value: worker.functionArn,
                exportName: stageConfig.getResourceName('ecfr-parser-worker-lambda-arn'),
            },
            EcfrParserLauncherLambdaArn: {
                value: launcher.functionArn,
                exportName: stageConfig.getResourceName('ecfr-parser-launcher-lambda-arn'),
            },
        };

        Object.entries(outputs).forEach(([name, cfg]) => new cdk.CfnOutput(this, name, cfg));
    }
}
