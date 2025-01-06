import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_lambda as lambda,
  aws_apigateway as apigateway,
  aws_logs as logs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as path from 'path';
import { StageConfig } from '../../config/stage-config';

export interface ApiConstructProps {
  vpc: ec2.IVpc;
  securityGroup: ec2.SecurityGroup;

  // Holds environment variables for the Lambda
  environmentConfig: {
    vpcId: string;
    logLevel: string;
    httpUser: string;
    httpPassword: string;
    subnetIds: string[];
  };

  storageBucketName: string;
  queueUrl: string;
  lambdaConfig: {
    memorySize: number;
    timeout: number;
    reservedConcurrentExecutions?: number;
  };

  pythonLayer: lambda.ILayerVersion;
  stageConfig: StageConfig;

  /**
   * Crucial fix:
   * Instead of just passing subnetIds as strings, we accept a SubnetSelection
   * so the Lambda will actually deploy into private subnets.
   */
  vpcSubnets: ec2.SubnetSelection;
}

export class ApiConstruct extends Construct {
  public readonly api: apigateway.RestApi;
  public readonly lambda: lambda.Function;

  constructor(scope: Construct, id: string, props: ApiConstructProps) {
    super(scope, id);

    // Create a dedicated log group for the API handler Lambda
    const logGroup = new logs.LogGroup(this, 'ApiHandlerLogGroup', {
      logGroupName: props.stageConfig.aws.lambda('api-handler'),
      retention: logs.RetentionDays.INFINITE,
    });

    // Create Lambda function in private subnets
    this.lambda = new lambda.Function(this, 'APIHandler', {
      functionName: props.stageConfig.getResourceName('api-handler'),
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.application',
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
      environment: {
        VPC_ID: props.environmentConfig.vpcId,
        LOG_LEVEL: props.environmentConfig.logLevel,
        HTTP_USER: props.environmentConfig.httpUser,
        HTTP_PASSWORD: props.environmentConfig.httpPassword,
        SUBNET_IDS: props.environmentConfig.subnetIds.join(','),
        AWS_STORAGE_BUCKET_NAME: props.storageBucketName,
        TEXT_EXTRACTOR_QUEUE_URL: props.queueUrl,
      },
      // **Important**: tie the Lambda to the provided VPC and subnets
      vpc: props.vpc,
      vpcSubnets: props.vpcSubnets,
      securityGroups: [props.securityGroup],
      layers: [props.pythonLayer],
      logRetention: logs.RetentionDays.INFINITE, // optional: ensure log retention matches your needs
    });

    // Create API Gateway log group
    const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
      logGroupName: props.stageConfig.aws.apiGateway('api'),
      retention: logs.RetentionDays.INFINITE,
    });

    // Create API Gateway
    this.api = new apigateway.RestApi(this, 'API', {
      restApiName: props.stageConfig.getResourceName('api'),
      description: 'eRegulations API Gateway',
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
        accessLogFormat: apigateway.AccessLogFormat.clf(),
      },
      // For uploading files (like PDFs)
      binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
    });

    // Add proxy integration to forward all routes to the Lambda
    const integration = new apigateway.LambdaIntegration(this.lambda, {
      proxy: true,
      allowTestInvoke: true,
    });

    this.api.root.addProxy({
      defaultIntegration: integration,
      anyMethod: true,
    });

    // Add customized 401 response for Unauthorized
    new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
      restApi: this.api,
      type: apigateway.ResponseType.UNAUTHORIZED,
      responseHeaders: {
        'WWW-Authenticate': "'Basic'",
      },
      statusCode: '401',
    });
  }
}

// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_lambda as lambda,
//   aws_apigateway as apigateway,
//   aws_logs as logs,
//   aws_iam as iam,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import * as path from 'path';
// import { StageConfig } from '../../config/stage-config';

// interface ApiConstructProps {
//   vpc: ec2.IVpc;
//   securityGroup: ec2.SecurityGroup;
//   environmentVariables: Record<string, string>;
//   lambdaConfig: {
//     memorySize: number;
//     timeout: number;
//     reservedConcurrentExecutions?: number;
//   };
//   pythonLayer: lambda.ILayerVersion;
//   stageConfig: StageConfig;
// }

// export class ApiConstruct extends Construct {
//   public readonly api: apigateway.RestApi;
//   public readonly lambda: lambda.Function;

//   constructor(scope: Construct, id: string, props: ApiConstructProps) {
//     super(scope, id);

//     const logGroup = new logs.LogGroup(this, 'ApiHandlerLogGroup', {
//       logGroupName: props.stageConfig.aws.lambda('api-handler'),
//       retention: logs.RetentionDays.INFINITE,
//     });

//     const lambdaRole = this.createLambdaRole(props.stageConfig, logGroup);

//     // Create Lambda function
//     this.lambda = new lambda.Function(this, 'APIHandler', {
//       functionName: props.stageConfig.getResourceName('api-handler'),
//       runtime: lambda.Runtime.PYTHON_3_12,
//       handler: 'handler.application',
//       code: lambda.Code.fromAsset(path.join(__dirname, '../api')),
//       memorySize: props.lambdaConfig.memorySize,
//       timeout: cdk.Duration.seconds(props.lambdaConfig.timeout),
//       reservedConcurrentExecutions: props.lambdaConfig.reservedConcurrentExecutions,
//       environment: props.environmentVariables,
//       vpc: props.vpc,
//       vpcSubnets: {
//         subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
//       },
//       securityGroups: [props.securityGroup],
//       layers: [props.pythonLayer],
//       role: lambdaRole,
//       logGroup,
//     });

//     // Create API Gateway Log Group
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
//       binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
//     });

//     // Add proxy integration
//     const integration = new apigateway.LambdaIntegration(this.lambda, {
//       proxy: true,
//       allowTestInvoke: true,
//     });

//     this.api.root.addProxy({
//       defaultIntegration: integration,
//       anyMethod: true,
//     });

//     // Add unauthorized response
//     new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
//       restApi: this.api,
//       type: apigateway.ResponseType.UNAUTHORIZED,
//       responseHeaders: {
//         'WWW-Authenticate': "'Basic'",
//       },
//       statusCode: '401',
//     });
//   }

//   private createLambdaRole(stageConfig: StageConfig, logGroup: logs.ILogGroup): iam.Role {
//     return new iam.Role(this, 'LambdaFunctionRole', {
//       path: stageConfig.iamPath,
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'PermissionsBoundary',
//         stageConfig.permissionsBoundaryArn
//       ),
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName(
//           'service-role/AWSLambdaVPCAccessExecutionRole'
//         ),
//       ],
//       inlinePolicies: {
//         LoggingPolicy: this.createLoggingPolicy(logGroup),
//       },
//     });
//   }

//   private createLoggingPolicy(logGroup: logs.ILogGroup): iam.PolicyDocument {
//     return new iam.PolicyDocument({
//       statements: [
//         new iam.PolicyStatement({
//           effect: iam.Effect.ALLOW,
//           actions: [
//             'logs:CreateLogStream',
//             'logs:PutLogEvents'
//           ],
//           resources: [
//             logGroup.logGroupArn,
//             `${logGroup.logGroupArn}:*`
//           ],
//         }),
//       ],
//     });
//   }
// }