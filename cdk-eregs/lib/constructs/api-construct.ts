import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_lambda as lambda,
  aws_apigateway as apigateway,
  aws_logs as logs,
  aws_iam as iam,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as path from 'path';
import { StageConfig } from '../../config/stage-config';

export interface ApiConstructProps {
  vpc: ec2.IVpc;
  securityGroup: ec2.SecurityGroup;
  environmentVariables: Record<string, string>;
  storageBucketName: string;
  queueUrl: string;
  lambdaConfig: {
    memorySize: number;
    timeout: number;
    reservedConcurrentExecutions?: number;
  };
  pythonLayer: lambda.ILayerVersion;
  stageConfig: StageConfig;
  vpcSubnets: ec2.SubnetSelection;
}

export class ApiConstruct extends Construct {
  public readonly api: apigateway.RestApi;
  public readonly lambda: lambda.Function;

  constructor(scope: Construct, id: string, props: ApiConstructProps) {
    super(scope, id);

    // Create log group for API handler Lambda
    const logGroup = new logs.LogGroup(this, 'ApiHandlerLogGroup', {
      logGroupName: props.stageConfig.aws.lambda('api-handler'),
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Create Lambda execution role with permissions matching serverless.yml
    const lambdaRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      path: '/service-role/'
    });

    // Add CloudWatch Logs permissions
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogStream',
        'logs:PutLogEvents',
      ],
      resources: [logGroup.logGroupArn],
    }));

    // Add SQS permissions matching serverless.yml
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['sqs:SendMessage'],
      resources: [props.queueUrl],
    }));

    // Add S3 permissions matching serverless.yml
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        's3:PutObject',
        's3:GetObject',
        's3:DeleteObject',
      ],
      resources: [
        `arn:aws:s3:::${props.storageBucketName}/*`,
      ],
    }));

    // Create Lambda function
    this.lambda = new lambda.Function(this, 'APIHandler', {
      functionName: props.stageConfig.getResourceName('api-handler'),
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend'), {
        exclude: [
          'node_modules/**',
          'nginx/**',
          '*.pyc',
          '__pycache__',
        ],
      }),
      memorySize: props.lambdaConfig.memorySize,
      timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
      reservedConcurrentExecutions: props.lambdaConfig.reservedConcurrentExecutions,
      environment: props.environmentVariables,
      vpc: props.vpc,
      vpcSubnets: props.vpcSubnets,
      securityGroups: [props.securityGroup],
      layers: [props.pythonLayer],
      role: lambdaRole,
      logRetention: logs.RetentionDays.ONE_MONTH,
      tracing: lambda.Tracing.ACTIVE,
    });

    // Create API Gateway log group
    const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: props.stageConfig.aws.apiGateway('api'),
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Create API Gateway with configuration matching serverless.yml
    this.api = new apigateway.RestApi(this, 'API', {
      restApiName: props.stageConfig.getResourceName('api'),
      description: 'eRegulations API Gateway',
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.clf(),
      },
      binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
    });

    // Add proxy integration
    const integration = new apigateway.LambdaIntegration(this.lambda, {
      proxy: true,
      allowTestInvoke: true,
    });

    this.api.root.addProxy({
      defaultIntegration: integration,
      anyMethod: true,
    });

    // Add customized 401 response matching serverless.yml
    new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
      restApi: this.api,
      type: apigateway.ResponseType.UNAUTHORIZED,
      responseHeaders: {
        'WWW-Authenticate': "'Basic'",
      },
      statusCode: '401',
    });

    // Add usage plan
    const plan = this.api.addUsagePlan('UsagePlan', {
      name: props.stageConfig.getResourceName('api-usage-plan'),
      throttle: {
        rateLimit: 10,
        burstLimit: 20,
      },
    });

    // Add tags
    cdk.Tags.of(this).add('Service', 'eregs-api');
    cdk.Tags.of(this).add('Environment', props.stageConfig.environment);
  }
}


// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_lambda as lambda,
//   aws_apigateway as apigateway,
//   aws_logs as logs,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import * as path from 'path';
// import { StageConfig } from '../../config/stage-config';

// export interface ApiConstructProps {
//   vpc: ec2.IVpc;
//   securityGroup: ec2.SecurityGroup;

//   // Holds environment variables for the Lambda
//   environmentConfig: {
//     vpcId: string;
//     logLevel: string;
//     httpUser: string;
//     httpPassword: string;
//     subnetIds: string[];
//   };

//   storageBucketName: string;
//   queueUrl: string;
//   lambdaConfig: {
//     memorySize: number;
//     timeout: number;
//     reservedConcurrentExecutions?: number;
//   };

//   pythonLayer: lambda.ILayerVersion;
//   stageConfig: StageConfig;

//   /**
//    * Crucial fix:
//    * Instead of just passing subnetIds as strings, we accept a SubnetSelection
//    * so the Lambda will actually deploy into private subnets.
//    */
//   vpcSubnets: ec2.SubnetSelection;
// }

// export class ApiConstruct extends Construct {
//   public readonly api: apigateway.RestApi;
//   public readonly lambda: lambda.Function;

//   constructor(scope: Construct, id: string, props: ApiConstructProps) {
//     super(scope, id);

//     // Create a dedicated log group for the API handler Lambda
//     const logGroup = new logs.LogGroup(this, 'ApiHandlerLogGroup', {
//       logGroupName: props.stageConfig.aws.lambda('api-handler'),
//       retention: logs.RetentionDays.INFINITE,
//     });

//     // Create Lambda function in private subnets
//     this.lambda = new lambda.Function(this, 'APIHandler', {
//       functionName: props.stageConfig.getResourceName('api-handler'),
//       runtime: lambda.Runtime.PYTHON_3_12,
//       handler: 'handler.lambda_handler',
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend'), {
//         exclude: [
//           'node_modules/**',
//           'nginx/**',
//           '*.pyc',
//           '__pycache__',
//         ],
//       }),
//       memorySize: props.lambdaConfig.memorySize,
//       timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
//       reservedConcurrentExecutions: props.lambdaConfig.reservedConcurrentExecutions,
//       environment: {
//         VPC_ID: props.environmentConfig.vpcId,
//         LOG_LEVEL: props.environmentConfig.logLevel,
//         HTTP_USER: props.environmentConfig.httpUser,
//         HTTP_PASSWORD: props.environmentConfig.httpPassword,
//         SUBNET_IDS: props.environmentConfig.subnetIds.join(','),
//         AWS_STORAGE_BUCKET_NAME: props.storageBucketName,
//         TEXT_EXTRACTOR_QUEUE_URL: props.queueUrl,
//       },
//       // **Important**: tie the Lambda to the provided VPC and subnets
//       vpc: props.vpc,
//       vpcSubnets: props.vpcSubnets,
//       securityGroups: [props.securityGroup],
//       layers: [props.pythonLayer],
//       logRetention: logs.RetentionDays.INFINITE, // optional: ensure log retention matches your needs
//     });

//     // Create API Gateway log group
//     const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
//       logGroupName: props.stageConfig.aws.apiGateway('api'),
//       retention: logs.RetentionDays.INFINITE,
//     });

//     // Create API Gateway
//     this.api = new apigateway.RestApi(this, 'API', {
//       restApiName: props.stageConfig.getResourceName('api'),
//       description: 'eRegulations API Gateway',
//       deployOptions: {
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
//         accessLogFormat: apigateway.AccessLogFormat.clf(),
//       },
//       // For uploading files (like PDFs)
//       binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
//     });

//     // Add proxy integration to forward all routes to the Lambda
//     const integration = new apigateway.LambdaIntegration(this.lambda, {
//       proxy: true,
//       allowTestInvoke: true,
//     });

//     this.api.root.addProxy({
//       defaultIntegration: integration,
//       anyMethod: true,
//     });

//     // Add customized 401 response for Unauthorized
//     new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
//       restApi: this.api,
//       type: apigateway.ResponseType.UNAUTHORIZED,
//       responseHeaders: {
//         'WWW-Authenticate': "'Basic'",
//       },
//       statusCode: '401',
//     });
//   }
// }

