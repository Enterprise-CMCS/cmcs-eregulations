// lib/constructs/parser-function.ts

import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { LambdaFunctionConstruct, DockerLambdaFunctionConstructProps } from './lambda-function-construct';

interface ParserFunctionProps {
  functionName: string;
  stage: string;
  vpc: ec2.IVpc;
  securityGroup: ec2.ISecurityGroup;
  dockerImagePath: string;
  schedule: string;
  eregsApiUrl: string;
  isEphemeral: boolean;
}

export class ParserFunction extends Construct {
  constructor(scope: Construct, id: string, props: ParserFunctionProps) {
    super(scope, id);

    const { functionName, stage, vpc, securityGroup, dockerImagePath, schedule, eregsApiUrl, isEphemeral } = props;

    // Create IAM role for the Lambda function
    const role = new iam.Role(this, `${functionName}Role`, {
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

    // Add inline policy to the role
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
      resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
    }));

    // Create Lambda function using the LambdaFunctionConstruct
    const lambdaProps: DockerLambdaFunctionConstructProps = {
      functionName,
      stage,
      vpc,
      codeType: 'docker',
      dockerImagePath,
      timeout: cdk.Duration.seconds(900),
      memorySize: 1024,
      environment: {
        STAGE: stage,
        PARSER_ON_LAMBDA: 'true',
        EREGS_USERNAME: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
        EREGS_PASSWORD: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
        EREGS_API_URL_V3: eregsApiUrl,
      },
      securityGroups: [securityGroup],
      role,
    };

    const lambdaFunction = new LambdaFunctionConstruct(this, `${functionName}Function`, lambdaProps);

    // Create EventBridge rule for scheduling
    new events.Rule(this, `${functionName}Schedule`, {
      schedule: events.Schedule.expression(schedule),
      targets: [new targets.LambdaFunction(lambdaFunction.function)],
    });

    // Set removal policy for Lambda function
    if (isEphemeral) {
      (lambdaFunction.function.node.defaultChild as cdk.CfnResource).cfnOptions.deletionPolicy = cdk.CfnDeletionPolicy.DELETE;
    }
  }
}