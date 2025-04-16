import * as cdk from 'aws-cdk-lib';
import {
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda,
    aws_events as events,
    aws_events_targets as targets,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import * as path from 'path';

interface LambdaConfig {
    runtime: lambda.Runtime;
    /** Memory allocation in MB for the Lambda function */
    memorySize: number;
    timeout: number;
}

interface EnvironmentConfig {
    secretName: string;
}

export interface ParserLauncherStackProps extends cdk.StackProps {
    lambdaConfig: LambdaConfig;
    environmentConfig: EnvironmentConfig;
}

export class ParserLauncherStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(
        scope: Construct,
        id: string,
        props: ParserLauncherStackProps,
        stageConfig: StageConfig
    ) {
        super(scope, id, props);

        // ================================
        // STACK IMPORTS
        // ================================
        const ecfrParserArn = cdk.Fn.importValue(`sls-${stageConfig.getResourceName('ecfr-parser')}-EcfrParserLambdaFunctionQualifiedArn`);
        const frParserArn = cdk.Fn.importValue(`sls-${stageConfig.getResourceName('fr-parser')}-FrParserLambdaFunctionQualifiedArn`);

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'ParserLauncherLogGroup', {
            logGroupName: stageConfig.aws.lambda('parser-launcher'),
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
                    resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
                }),
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: [
                        'lambda:InvokeFunction',
                    ],
                    resources: [ecfrParserArn, frParserArn],
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
                LambdaPolicy: lambdaPolicy,
            },
        });

        // ================================
        // LAMBDA FUNCTION
        // ================================
        const lambdaFunction = new lambda.DockerImageFunction(this, 'ParserLauncherFunction', {
            functionName: stageConfig.getResourceName('parser-launcher'),
            code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/parser/launcher/'), {
                file: 'Dockerfile',
            }),
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout || 900),
            memorySize: props.lambdaConfig.memorySize,
            environment: {
                STAGE_ENV: stageConfig.stageName,
                SECRET_NAME: props.environmentConfig.secretName,
                ECFR_PARSER_ARN: ecfrParserArn,
                FR_PARSER_ARN: frParserArn,
            },
            role: lambdaRole,
        });

        // ================================
        // CLOUDWATCH EVENT RULE
        // ================================
        const rule = new events.Rule(this, 'ParserLauncherSchedule', {
            schedule: events.Schedule.expression('cron(0 0 * * ? *)'),  // Midnight every day
            enabled: true,
        });
        rule.addTarget(new targets.LambdaFunction(lambdaFunction));

        // ================================
        // STACK OUTPUTS
        // ================================
        new cdk.CfnOutput(this, 'ParserLauncherLambdaFunctionQualifiedArn', {
            value: lambdaFunction.currentVersion.functionArn,
            description: 'Current Lambda function version',
            exportName: `sls-${stageConfig.getResourceName('parser-launcher')}-ParserLauncherLambdaFunctionQualifiedArn`,
        });
    }
}
