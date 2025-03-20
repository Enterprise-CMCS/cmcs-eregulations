import * as cdk from 'aws-cdk-lib';
import {
  aws_iam as iam,
  aws_logs as logs,
  aws_lambda as lambda,
  aws_events as events,
  aws_events_targets as targets,
  aws_ec2 as ec2,
  Tags,
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

    // eCFR and FR ARNs
    const ecfrParserArn = cdk.Fn.importValue(`sls-${stageConfig.getResourceName('ecfr-parser')}-EcfrParserLambdaFunctionQualifiedArn`);
    const frParserArn = cdk.Fn.importValue(`sls-${stageConfig.getResourceName('fr-parser')}-FrParserLambdaFunctionQualifiedArn`);

    // Create Lambda infrastructure
    const { lambdaRole, logGroup } = this.createLambdaInfrastructure(stageConfig, ecfrParserArn, frParserArn);

    // Create Lambda function
    this.lambda = new lambda.Function(this, 'ParserLauncherFunction', {
        functionName: stageConfig.getResourceName('parser-launcher'),
        runtime: props.lambdaConfig.runtime,
        handler: 'parser_launcher.handler',
        code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/parser/')),
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

    // Create CloudWatch Event Rule
    const rule = new events.Rule(this, 'ParserLauncherSchedule', {
      schedule: events.Schedule.expression('cron(0 0 * * ? *)'),  // Midnight every day
      enabled: true,
    });

    rule.addTarget(new targets.LambdaFunction(this.lambda));

    // Create stack outputs
    this.createStackOutputs(stageConfig);
  }

  private createLambdaInfrastructure(stageConfig: StageConfig, ecfrParserArn: string, frParserArn: string) {
    const logGroup = new logs.LogGroup(this, 'ParserLauncherLogGroup', {
      logGroupName: stageConfig.aws.lambda('parser-launcher'),
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
        LambdaPolicy: this.createLambdaPolicy(ecfrParserArn, frParserArn),
      },
    });

    return { lambdaRole, logGroup };
  }

  private createLambdaPolicy(ecfrParserArn: string, frParserArn: string): iam.PolicyDocument {
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
        new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'lambda:InvokeFunction',
            ],
            resources: [ecfrParserArn, frParserArn],
        }),
      ],
    });
  }

  private createStackOutputs(stageConfig: StageConfig) {
    // Output the Lambda function ARN
    new cdk.CfnOutput(this, 'ParserLauncherLambdaFunctionQualifiedArn', {
      value: this.lambda.currentVersion.functionArn,
      description: 'Current Lambda function version',
      exportName: `sls-${stageConfig.getResourceName('parser-launcher')}-ParserLauncherLambdaFunctionQualifiedArn`,
    });
  }
}
