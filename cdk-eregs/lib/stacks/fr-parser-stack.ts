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

export interface FrParserStackProps extends cdk.StackProps {
  lambdaConfig: LambdaConfig;
  environmentConfig: EnvironmentConfig;
}

export class FrParserStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(
        scope: Construct,
        id: string,
        props: FrParserStackProps,
        stageConfig: StageConfig
    ) {
        super(scope, id, props);

        // Create Lambda infrastructure
        const { lambdaRole } = this.createLambdaInfrastructure(stageConfig);

        // Get the API Gateway endpoint from stack outputs
        const siteEndpoint = cdk.Fn.importValue(stageConfig.getResourceName('api-endpoint'));

        // Create Lambda function
        this.lambda = new lambda.DockerImageFunction(this, 'FrParserFunction', {
            functionName: stageConfig.getResourceName('fr-parser'),
            code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/parser/'), {
                file: 'fr-parser/Dockerfile',
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

        // DISABLED for now
        // // Create CloudWatch Event Rule
        // const rule = new events.Rule(this, 'FrParserSchedule', {
        //   schedule: events.Schedule.expression('cron(0 2 * * ? *)'),
        //   enabled: true,
        // });
        // rule.addTarget(new targets.LambdaFunction(this.lambda));

        // Create stack outputs
        this.createStackOutputs(stageConfig);
    }

    private createLambdaInfrastructure(stageConfig: StageConfig) {
        const logGroup = new logs.LogGroup(this, 'FrParserLogGroup', {
            logGroupName: stageConfig.aws.lambda('fr-parser'),
            retention: logs.RetentionDays.INFINITE,
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
                LambdaPolicy: this.createLambdaPolicy(),
            },
        });

        return { lambdaRole, logGroup };
    }

    private createLambdaPolicy(): iam.PolicyDocument {
        return new iam.PolicyDocument({
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
    }

    private createStackOutputs(stageConfig: StageConfig) {
        // Output the Lambda function ARN
        new cdk.CfnOutput(this, 'FrParserLambdaFunctionQualifiedArn', {
            value: this.lambda.functionArn,
            description: 'Current Lambda function version',
            exportName: `sls-${stageConfig.getResourceName('fr-parser')}-FrParserLambdaFunctionQualifiedArn`,
        });
    }
}
