// src/stacks/redirect/redirect-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as logs from 'aws-cdk-lib/aws-logs';
import { BaseStack } from './base-stack';
import { Environment, StackUtils } from '../../config/types/config-types';
export interface RedirectStackProps extends cdk.StackProps {
  stage: Environment;
  prNumber?: string;
}

/**
 * Redirect API Stack implementation
 * Can be used as a template for other API stacks
 */
export class RedirectStack extends BaseStack {
  private lambdaFunction?: lambda.Function;
  private api?: apigateway.RestApi;

  constructor(scope: Construct, id: string, props: RedirectStackProps) {
    super(scope, id, {
      name: 'redirect',
      stage: props.stage,
      prNumber: props.prNumber,
      isExperimental: StackUtils.isExperimentalDeployment(props.prNumber),
    }, props);

    this.createResources();
    this.addOutputs();
  }

  protected createResources(): void {
    this.createLambdaFunction();
    this.createApiGateway();
  }

  private createLambdaFunction(): void {
    const role = new iam.Role(this, 'LambdaRole', {
      roleName: this.getResourceName('role', 'redirect'),
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      path: this.parameterStore.getParameter('BASE', 'IAM_PATH'),
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        this.parameterStore.getParameter('BASE', 'PERMISSIONS_BOUNDARY')
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AWSLambdaBasicExecutionRole'
        ),
      ],
    });

    this.lambdaFunction = new lambda.Function(this, 'RedirectFunction', {
      functionName: this.getResourceName('function', 'redirect'),
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'redirect_lambda.handler',
      code: lambda.Code.fromAsset('../lambda/redirect'),
      memorySize: 128,
      timeout: cdk.Duration.seconds(30),
      environment: {
        STAGE: this.stackPrefix,
      },
      role,
      tracing: lambda.Tracing.ACTIVE,
    });

    new logs.LogGroup(this, 'LambdaLogGroup', {
      logGroupName: `/aws/lambda/${this.lambdaFunction.functionName}`,
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: this.removalPolicy,
    });
  }

  private createApiGateway(): void {
    this.api = new apigateway.RestApi(this, 'RedirectApi', {
      restApiName: this.getResourceName('api', 'redirect'),
      description: 'Redirect API Service',
      deployOptions: {
        stageName: this.config.stage,
        tracingEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
      },
      binaryMediaTypes: [
        'multipart/form-data',
        'application/pdf',
      ],
    });

    this.api.root.addProxy({
      defaultIntegration: new apigateway.LambdaIntegration(this.lambdaFunction!),
      anyMethod: true,
    });
  }

  private addOutputs(): void {
    if (this.lambdaFunction) {
      new cdk.CfnOutput(this, 'LambdaArn', {
        value: this.lambdaFunction.functionArn,
        description: 'Redirect Lambda Function ARN',
        exportName: `${this.stackPrefix}-redirect-lambda-arn`,
      });
    }

    if (this.api) {
      new cdk.CfnOutput(this, 'ApiUrl', {
        value: this.api.url,
        description: 'Redirect API Gateway URL',
        exportName: `${this.stackPrefix}-redirect-api-url`,
      });
    }
  }
}
