// lib/stacks/maintenance-lambda-stack.ts

import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as path from 'path';
import { Construct } from 'constructs';

interface MaintenanceLambdaStackProps extends cdk.StackProps {
  stage: string;
}

export class MaintenanceLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: MaintenanceLambdaStackProps) {
    super(scope, id, props);

    const { stage } = props;

    // IAM Role for the Lambda function
    const lambdaRole = new iam.Role(this, 'MaintenanceLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    });

    // Add SSM Parameter for permissions boundary if needed
    const permissionsBoundaryArn = ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/permissions_boundary_policy');
    lambdaRole.addManagedPolicy(
      iam.ManagedPolicy.fromManagedPolicyArn(this, 'PermissionsBoundary', permissionsBoundaryArn),
    );

    // Lambda Function for Maintenance
    const maintenanceLambda = new lambda.Function(this, 'MaintenanceLambdaFunction', {
      runtime: lambda.Runtime.PYTHON_3_9, // Adjust as needed
      handler: 'maintenance.handler', // Match your handler in the Lambda function code
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')), // Assuming lambda code is in `lambda/maintenance`
      functionName: `MaintenanceLambda-${stage}`,
      timeout: cdk.Duration.seconds(60),
      memorySize: 256,
      role: lambdaRole,
      environment: {
        STAGE: stage,
      },
    });

    // API Gateway REST API for Maintenance Endpoint
    const api = new apigateway.RestApi(this, 'MaintenanceApi', {
      restApiName: `MaintenanceAPI-${stage}`,
      description: `API Gateway for Maintenance Lambda in ${stage} environment`,
      deployOptions: {
        stageName: stage,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        metricsEnabled: true,
      },
    });

    // Connect API Gateway to the Lambda
    const maintenanceResource = api.root.addResource('maintenance');
    const lambdaIntegration = new apigateway.LambdaIntegration(maintenanceLambda);
    maintenanceResource.addMethod('GET', lambdaIntegration); // Assuming GET method for maintenance endpoint

    // Outputs
    new cdk.CfnOutput(this, 'MaintenanceLambdaFunctionArn', {
      value: maintenanceLambda.functionArn,
      description: 'ARN of the Maintenance Lambda function',
    });

    new cdk.CfnOutput(this, 'MaintenanceApiUrl', {
      value: api.url,
      description: 'URL of the Maintenance API Gateway',
    });
  }
}
