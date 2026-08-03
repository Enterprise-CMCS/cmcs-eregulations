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

export interface FrParserStackProps extends cdk.StackProps {
    lambdaConfig: LambdaConfig;
    environmentConfig: EnvironmentConfig;
}

export class FrParserStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: FrParserStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        const siteEndpoint = cdk.Fn.importValue(stageConfig.getResourceName('api-endpoint'));

        const deadLetterQueue = new sqs.Queue(this, 'FrParserDeadLetterQueue', {
            queueName: stageConfig.getResourceName('fr-parser-dlq'),
            retentionPeriod: cdk.Duration.days(14),
        });

        const queue = new sqs.Queue(this, 'FrParserQueue', {
            queueName: stageConfig.getResourceName('fr-parser-queue'),
            visibilityTimeout: cdk.Duration.seconds(900),
            retentionPeriod: cdk.Duration.days(14),
            deadLetterQueue: {
                queue: deadLetterQueue,
                maxReceiveCount: 5,
            },
        });

        new logs.LogGroup(this, 'FrParserWorkerLogGroup', {
            logGroupName: stageConfig.aws.lambda('fr-parser-worker'),
            retention: logs.RetentionDays.INFINITE,
        });

        new logs.LogGroup(this, 'FrParserLauncherLogGroup', {
            logGroupName: stageConfig.aws.lambda('fr-parser-launcher'),
            retention: logs.RetentionDays.INFINITE,
        });

        const worker = new lambda.DockerImageFunction(this, 'FrParserWorkerFunction', {
            functionName: stageConfig.getResourceName('fr-parser-worker'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'parsers/fr-worker/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                EREGS_API_URL_V3: `${siteEndpoint}v3/`,
                EREGS_AUTH_SECRET_NAME: props.environmentConfig.authSecretName,
            },
        });

        const launcher = new lambda.DockerImageFunction(this, 'FrParserLauncherFunction', {
            functionName: stageConfig.getResourceName('fr-parser-launcher'),
            code: lambda.DockerImageCode.fromImageAsset(path.resolve(__dirname, '../../../solution/'), {
                file: 'parsers/fr-launcher/Dockerfile',
            }),
            memorySize: props.lambdaConfig.memorySize,
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
            environment: {
                LOG_LEVEL: props.environmentConfig.logLevel,
                EREGS_API_URL_V3: `${siteEndpoint}v3/`,
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

        new lambda.EventSourceMapping(this, 'FrParserWorkerEventSource', {
            target: worker,
            batchSize: 1,
            eventSourceArn: queue.queueArn,
            enabled: true,
        });

        const rule = new events.Rule(this, 'FrParserLauncherSchedule', {
            schedule: events.Schedule.expression('cron(5 0 * * ? *)'),
            enabled: true,
        });
        rule.addTarget(new targets.LambdaFunction(launcher));

        const outputs: Record<string, cdk.CfnOutputProps> = {
            FrParserQueueArn: {
                value: queue.queueArn,
                exportName: stageConfig.getResourceName('fr-parser-queue-arn'),
            },
            FrParserQueueUrl: {
                value: queue.queueUrl,
                exportName: stageConfig.getResourceName('fr-parser-queue-url'),
            },
            FrParserDlqArn: {
                value: deadLetterQueue.queueArn,
                exportName: stageConfig.getResourceName('fr-parser-dlq-arn'),
            },
            FrParserWorkerLambdaArn: {
                value: worker.functionArn,
                exportName: stageConfig.getResourceName('fr-parser-worker-lambda-arn'),
            },
            FrParserLauncherLambdaArn: {
                value: launcher.functionArn,
                exportName: stageConfig.getResourceName('fr-parser-launcher-lambda-arn'),
            },
        };

        Object.entries(outputs).forEach(([name, cfg]) => new cdk.CfnOutput(this, name, cfg));
    }
}
