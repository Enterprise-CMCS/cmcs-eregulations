import * as cdk from 'aws-cdk-lib';
import {
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda as lambda,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import * as path from 'path';

interface LambdaConfig {
    /** Memory allocation in MB for the Lambda function */
    memorySize: number;
    timeout: number;
}

interface EnvironmentConfig {
    logLevel: string;
}

export interface EcfrParserStackProps extends cdk.StackProps {
    lambdaConfig: LambdaConfig;
    environmentConfig: EnvironmentConfig;
}

export class EcfrParserStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(
        scope: Construct,
        id: string,
        props: EcfrParserStackProps,
        stageConfig: StageConfig
    ) {
        super(scope, id, props);

        // ================================
        // LOG GROUP
        // ================================
        new logs.LogGroup(this, 'EcfrParserLogGroup', {
            logGroupName: stageConfig.aws.lambda('ecfr-parser'),
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

        // Get the API Gateway endpoint from stack outputs
        const siteEndpoint = cdk.Fn.importValue(stageConfig.getResourceName('api-endpoint'))

        const lambdaFunction = new lambda.DockerImageFunction(this, 'EcfrParserFunction', {
            functionName: stageConfig.getResourceName('ecfr-parser'),
            code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/parser/'), {
                file: 'ecfr-parser/Dockerfile',
            }),
            timeout: cdk.Duration.seconds(props.lambdaConfig.timeout || 900),
            memorySize: props.lambdaConfig.memorySize,
            environment: {
                PARSER_ON_LAMBDA: 'true',
                EREGS_API_URL_V3: `${siteEndpoint}v3/`,
                STAGE_ENV: stageConfig.stageName,
                LOG_LEVEL: props.environmentConfig.logLevel,
            },
            role: lambdaRole,
        });

        // ================================
        // CLOUDWATCH EVENT RULE
        // ================================
        // DISABLED for now
        // // Create CloudWatch Event Rule - note different cron expression
        // const rule = new events.Rule(this, 'EcfrParserSchedule', {
        //   schedule: events.Schedule.expression('cron(0 0 * * ? *)'),  // Midnight every day
        //   enabled: true,
        // });
        // rule.addTarget(new targets.LambdaFunction(lambdaFunction));

        // ================================
        // STACK OUTPUTS
        // ================================
        new cdk.CfnOutput(this, 'EcfrParserLambdaFunctionQualifiedArn', {
            value: lambdaFunction.functionArn,
            description: 'Current Lambda function version',
            exportName: `sls-${stageConfig.getResourceName('ecfr-parser')}-EcfrParserLambdaFunctionQualifiedArn`,
        });
    }
}
