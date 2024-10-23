import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';
import { BaseStack } from './base-stack';
import { Environment, StackUtils } from '../../config/types/config-types';

/**
 * Props interface for the MaintenanceStack.
 * Extends the basic CDK stack props with additional
 * properties needed for our deployment patterns.
 */
export interface MaintenanceStackProps extends cdk.StackProps {
  /** Deployment environment (dev, val, prod) */
  stage: Environment;
  /** PR number for experimental deployments */
  prNumber?: string;
}

/**
 * MaintenanceStack implements a simple API endpoint that can be used
 * for maintenance mode or health checks. This implementation mirrors
 * the configuration from serverless.yml while using CDK constructs.
 * 
 * Features:
 * - Python Lambda function with basic request handling
 * - API Gateway with proxy integration
 * - IAM role with proper permissions and boundary
 * - CloudWatch logs configuration
 * - Support for experimental (PR-based) deployments
 * 
 * @example
 * ```typescript
 * new MaintenanceStack(app, 'maintenance-stack', {
 *   stage: 'dev',
 *   prNumber: '123', // Optional, for experimental deployments
 * });
 * ```
 */
export class MaintenanceStack extends BaseStack {
  /** Lambda function that handles the maintenance endpoint */
  private lambdaFunction?: lambda.Function;
  /** API Gateway that exposes the Lambda function */
  private api?: apigateway.RestApi;

  constructor(scope: Construct, id: string, props: MaintenanceStackProps) {
    super(scope, id, {
      name: 'maintenance',
      stage: props.stage,
      prNumber: props.prNumber,
      isExperimental: StackUtils.isExperimentalDeployment(props.prNumber),
    }, props);

    this.createResources();
    this.addOutputs();
  }

  /**
   * Creates all resources for the maintenance stack.
   * This includes the Lambda function and API Gateway.
   * @protected
   */
  protected createResources(): void {
    this.createLambdaFunction();
    this.createApiGateway();
  }

  /**
   * Creates the Lambda function and its associated role.
   * The function is configured with basic Python runtime
   * and proper permissions for logging and execution.
   * @private
   */
  private createLambdaFunction(): void {
    // Create IAM role for Lambda function
    const role = new iam.Role(this, 'LambdaRole', {
      roleName: this.getResourceName('role', 'maintenance'),
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      // Fetch IAM path from SSM parameter store
      path: this.parameterStore.getParameter('BASE', 'IAM_PATH'),
      // Fetch and apply permissions boundary from SSM
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        this.parameterStore.getParameter('BASE', 'PERMISSIONS_BOUNDARY')
      ),
      // Apply required managed policies
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AWSLambdaVPCAccessExecutionRole'
        ),
      ],
    });

    // Add CloudWatch Logs permissions
    role.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'logs:CreateLogGroup',
          'logs:CreateLogStream',
          'logs:PutLogEvents',
        ],
        resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
      })
    );

    // Create Lambda function
    this.lambdaFunction = new lambda.Function(this, 'MaintenanceFunction', {
      functionName: this.getResourceName('function', 'maintenance'),
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'maintenance_lambda.handler',
      code: lambda.Code.fromAsset('../lambda/maintenance'),
      memorySize: 128,
      timeout: cdk.Duration.seconds(30),
      environment: {
        STAGE: this.stackPrefix,
      },
      role,
      tracing: lambda.Tracing.ACTIVE,
    });

    // Create CloudWatch log group with retention
    new logs.LogGroup(this, 'LambdaLogGroup', {
      logGroupName: `/aws/lambda/${this.lambdaFunction.functionName}`,
      retention: logs.RetentionDays.ONE_MONTH,
      // Use stack's removal policy (DESTROY for experimental, RETAIN for regular deployments)
      removalPolicy: this.removalPolicy,
    });
  }

  /**
   * Creates the API Gateway with proxy integration to the Lambda function.
   * Configures binary media types and logging as specified in serverless.yml.
   * @private
   */
  private createApiGateway(): void {
    this.api = new apigateway.RestApi(this, 'MaintenanceApi', {
      restApiName: this.getResourceName('api', 'maintenance'),
      description: 'Maintenance API Service',
      deployOptions: {
        stageName: this.config.stage,
        tracingEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
      },
      // Match binary media types from serverless.yml
      binaryMediaTypes: [
        'multipart/form-data',
        'application/pdf',
      ],
    });

    // Add proxy integration to handle all methods and paths
    this.api.root.addProxy({
      defaultIntegration: new apigateway.LambdaIntegration(this.lambdaFunction!),
      anyMethod: true,
    });
  }

  /**
   * Adds CloudFormation outputs for the stack resources.
   * These outputs can be used by other stacks or for reference.
   * @private
   */
  private addOutputs(): void {
    // Output Lambda ARN
    if (this.lambdaFunction) {
      new cdk.CfnOutput(this, 'LambdaArn', {
        value: this.lambdaFunction.functionArn,
        description: 'Maintenance Lambda Function ARN',
        exportName: `${this.stackPrefix}-maintenance-lambda-arn`,
      });
    }

    // Output API Gateway URL
    if (this.api) {
      new cdk.CfnOutput(this, 'ApiUrl', {
        value: this.api.url,
        description: 'Maintenance API Gateway URL',
        exportName: `${this.stackPrefix}-maintenance-api-url`,
      });
    }
  }
}
