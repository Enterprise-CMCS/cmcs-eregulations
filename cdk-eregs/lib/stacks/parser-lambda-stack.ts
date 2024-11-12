
// lib/stacks/parser-stack.ts

import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';
import { LambdaFunctionConstruct, DockerLambdaFunctionConstructProps } from '../constructs/lambda-function-construct';
import { EnvironmentConfig } from '../../config/environment-config';

interface ParserStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
  vpc: ec2.IVpc;
}

export class ParserStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ParserStackProps) {
    super(scope, id, props);

    const { config, vpc } = props;

    // Create IAM Role for Lambda functions
    const lambdaRole = this.createLambdaRole(config);

    // Create ECFR Parser Lambda
    const ecfrParser = this.createParserLambda('ecfr', lambdaRole, vpc, config);

    // Create FR Parser Lambda
    const frParser = this.createParserLambda('fr', lambdaRole, vpc, config);

    // Create EventBridge Rules for scheduling
    this.createScheduleRule('ECFRParserSchedule', 'cron(0 0 * * ? *)', ecfrParser.function);
    this.createScheduleRule('FRParserSchedule', 'cron(0 2 * * ? *)', frParser.function);

    // Create Security Group
    new ec2.SecurityGroup(this, 'ParserSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Parser Lambda Functions',
      allowAllOutbound: true,
    });
  }

  private createLambdaRole(config: EnvironmentConfig): iam.Role {
    const role = new iam.Role(this, 'ParserLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/path'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        `arn:aws:iam::${this.account}:policy${ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/permissions_boundary_policy')}`
      ),
    });

    // Add inline policies
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogGroup',
        'logs:CreateLogStream',
        'logs:PutLogEvents',
      ],
      resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*`],
    }));

    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:PutObject'],
      resources: [`arn:aws:s3:::${this.artifactsBucketName}`],
    }));

    return role;
  }

  private createParserLambda(
    parserType: 'ecfr' | 'fr',
    role: iam.IRole,
    vpc: ec2.IVpc,
    config: EnvironmentConfig
  ): LambdaFunctionConstruct {
    const eregsUrl = cdk.Fn.importValue(`cmcs-eregs-site-${config.stackPrefix}-ServiceEndpoint`);

    const lambdaProps: DockerLambdaFunctionConstructProps = {
      functionName: `${parserType}-parser`,
      stage: config.stackPrefix,
      vpc,
      codeType: 'docker',
      dockerImagePath: `./${parserType}-parser`,
      timeout: cdk.Duration.seconds(900),
      memorySize: 1024,  // Adjust as needed
      environment: {
        STAGE: config.stackPrefix,
        PARSER_ON_LAMBDA: 'true',
        EREGS_USERNAME: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
        EREGS_PASSWORD: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
        EREGS_API_URL_V3: `${eregsUrl}/v3/`,
        STAGE_ENV: config.stackPrefix,
      },
      role,
    };

    return new LambdaFunctionConstruct(this, `${parserType.toUpperCase()}ParserLambda`, lambdaProps);
  }

  private createScheduleRule(id: string, scheduleExpression: string, lambdaFunction: cdk.aws_lambda.IFunction) {
    const rule = new events.Rule(this, id, {
      schedule: events.Schedule.expression(scheduleExpression),
    });
    rule.addTarget(new targets.LambdaFunction(lambdaFunction));
  }
}