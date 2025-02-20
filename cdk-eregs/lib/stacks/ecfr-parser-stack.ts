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
  timeout: number;
}

interface EnvironmentConfig {
  httpUser: string;
  httpPassword: string;
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

    // Create Lambda infrastructure
    const { lambdaRole, logGroup } = this.createLambdaInfrastructure(stageConfig);

    // Get the site stack endpoint using stageConfig
    // const siteEndpoint = cdk.Fn.importValue(`${stageConfig.getResourceName('site')}-ServiceEndpoint`);
      // Get the API Gateway endpoint from stack outputs
      // Get API endpoint and trim any trailing slash
      const siteEndpoint = cdk.Fn.importValue(
        stageConfig.getResourceName('api-endpoint')
      )
    // Create Lambda function
    this.lambda = new lambda.DockerImageFunction(this, 'EcfrParserFunction', {
      functionName: stageConfig.getResourceName('ecfr-parser'),
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/parser/'), {
        file: 'ecfr-parser/Dockerfile',

      }),
      timeout: cdk.Duration.seconds(props.lambdaConfig.timeout || 900),
      environment: {
        PARSER_ON_LAMBDA: 'true',
        EREGS_USERNAME: props.environmentConfig.httpUser,
        EREGS_PASSWORD: props.environmentConfig.httpPassword,
        EREGS_API_URL_V3: `${siteEndpoint}v3/`,
        STAGE_ENV: stageConfig.stageName,
        LOG_LEVEL: props.environmentConfig.logLevel,
      },
      role: lambdaRole,
    });

    // Create CloudWatch Event Rule - note different cron expression
    const rule = new events.Rule(this, 'EcfrParserSchedule', {
      schedule: events.Schedule.expression('cron(0 0 * * ? *)'),  // Midnight every day
      enabled: true,
    });

    rule.addTarget(new targets.LambdaFunction(this.lambda));

    // Create stack outputs
    this.createStackOutputs(stageConfig);
  }

  private createLambdaInfrastructure(stageConfig: StageConfig) {
    const logGroup = new logs.LogGroup(this, 'EcfrParserLogGroup', {
      logGroupName: stageConfig.aws.lambda('ecfr-parser'),
      retention: logs.RetentionDays.ONE_MONTH,
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
    new cdk.CfnOutput(this, 'EcfrParserLambdaFunctionQualifiedArn', {
      value: this.lambda.currentVersion.functionArn,
      description: 'Current Lambda function version',
      exportName: `sls-${stageConfig.getResourceName('ecfr-parser')}-EcfrParserLambdaFunctionQualifiedArn`,
    });
  }
}
