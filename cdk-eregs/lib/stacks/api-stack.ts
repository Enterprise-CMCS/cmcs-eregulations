import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_s3 as s3,
  aws_lambda as lambda,
  aws_sqs as sqs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import { DatabaseConstruct } from '../constructs/database-construct';
import { ApiConstruct } from '../constructs/api-construct';
import { WafConstruct } from '../constructs/waf-construct';

interface APIStackProps extends cdk.StackProps {
  lambdaConfig: {
    memorySize: number;
    timeout: number;
    reservedConcurrentExecutions?: number;
  };
  environmentConfig: {
    vpcId: string;
    logLevel: string;
    httpUser: string;
    httpPassword: string;
    subnetIds: string[];  // [privateSubnetAId, privateSubnetBId]
  };
}

export class APIStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
    super(scope, id, props);

    // Create storage bucket
    const storageBucket = new s3.Bucket(this, 'StorageBucket', {
      bucketName: `file-repo-eregs`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      cors: [
        {
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
          allowedOrigins: ['*'],
          allowedHeaders: ['*'],
          maxAge: 3000,
        },
      ],
    });

    // Look up VPC by ID
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId,
    });

    // Convert your array of subnet IDs into a SubnetSelection
    // so we can actually deploy resources into those subnets.
    const selectedSubnets: ec2.SubnetSelection = {
      subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
        ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
      ),
    };

    // Security group for Lambda / API
    // (Adjust egress rules if you want to restrict external calls further)
    const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions (Lambda/API)',
      allowAllOutbound: true,
    });

    // Security group for Database
    // (We set outbound to false to reduce exfil risk from the DB side)
    const dbSG = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Aurora Database',
      allowAllOutbound: false,
    });

    // Allow inbound PostgreSQL from the Lambda SG only
    dbSG.addIngressRule(
      serverlessSG,
      ec2.Port.tcp(5432),
      'Allow PostgreSQL access from Lambda functions',
    );

    // Import external resources
    const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
      this,
      'SharedPythonLayer',
      cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn')),
    );

    const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
      queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
      queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
    });

    // Create the Database in the private subnets
    const database = new DatabaseConstruct(this, 'Database', {
      vpc,
      dbPassword: props.environmentConfig.httpPassword,
      securityGroup: dbSG,
      // Pass our SubnetSelection
      vpcSubnets: selectedSubnets,
    });

    // Create the API (Lambda + API Gateway) also in the private subnets
    const api = new ApiConstruct(this, 'Api', {
      vpc,
      securityGroup: serverlessSG,
      environmentConfig: {
        vpcId: props.environmentConfig.vpcId,
        logLevel: props.environmentConfig.logLevel,
        httpUser: props.environmentConfig.httpUser,
        httpPassword: props.environmentConfig.httpPassword,
        subnetIds: props.environmentConfig.subnetIds,
      },
      storageBucketName: storageBucket.bucketName,
      queueUrl: textExtractorQueue.queueUrl,
      lambdaConfig: props.lambdaConfig,
      pythonLayer,
      stageConfig,
      // Same subnets for the API’s Lambda
      vpcSubnets: selectedSubnets,
    });

    // Create the WAF
    const waf = new WafConstruct(this, 'Waf', stageConfig);

    // Stack outputs
    const outputs: Record<string, cdk.CfnOutputProps> = {
      ApiHandlerArn: {
        value: api.lambda.functionArn,
        description: 'API Handler Lambda function ARN',
        exportName: stageConfig.getResourceName('api-handler-arn'),
      },
      ApiHandlerName: {
        value: api.lambda.functionName,
        description: 'API Handler Lambda function name',
        exportName: stageConfig.getResourceName('api-handler-name'),
      },
      ApiEndpoint: {
        value: api.api.url,
        description: 'API Gateway endpoint URL',
        exportName: stageConfig.getResourceName('api-endpoint'),
      },
      ApiLogGroup: {
        value: stageConfig.aws.apiGateway('api'),
        description: 'API Gateway Log Group name',
        exportName: stageConfig.getResourceName('api-log-group'),
      },
      LambdaLogGroup: {
        value: stageConfig.aws.lambda('api-handler'),
        description: 'Lambda Log Group name',
        exportName: stageConfig.getResourceName('lambda-log-group'),
      },
      DatabaseEndpoint: {
        value: database.dbCluster.clusterEndpoint.hostname,
        description: 'Database cluster endpoint',
        exportName: stageConfig.getResourceName('db-endpoint'),
      },
      StorageBucketName: {
        value: storageBucket.bucketName,
        description: 'Storage bucket name',
        exportName: stageConfig.getResourceName('storage-bucket-name'),
      },
    };

    Object.entries(outputs).forEach(([name, config]) => new cdk.CfnOutput(this, name, config));
  }
}

// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_s3 as s3,
//   aws_lambda as lambda,
//   aws_apigateway as apigateway,
//   aws_logs as logs,
//   aws_iam as iam,
//   aws_sqs as sqs,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';
// import { DatabaseConstruct } from '../constructs/database-construct';
// import { ApiConstruct } from '../constructs/api-construct';
// import { WafConstruct } from '../constructs/waf-construct';

// interface APIStackProps extends cdk.StackProps {
//   lambdaConfig: {
//     memorySize: number;
//     timeout: number;
//     reservedConcurrentExecutions?: number;
//   };
//   environmentConfig: {
//     vpcId: string;
//     logLevel: string;
//     httpUser: string;
//     httpPassword: string;
//     subnetIds: string[];
//   };
// }

// export class APIStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     // Create storage bucket with standardized naming
//     const storageBucket = new s3.Bucket(this, 'StorageBucket', {
//       bucketName: `file-repo-eregs`,
//       encryption: s3.BucketEncryption.S3_MANAGED,
//       blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
//       enforceSSL: true,
//       cors: [{
//         allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
//         allowedOrigins: ['*'],
//         allowedHeaders: ['*'],
//         maxAge: 3000,
//       }],
//     });

//     // Use VPC from SSM parameters
//     const vpc = ec2.Vpc.fromVpcAttributes(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//       availabilityZones: [`${this.region}a`, `${this.region}b`],
//       privateSubnetIds: props.environmentConfig.subnetIds,
//     });

//     // Create security groups
//     const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Serverless Functions',
//       allowAllOutbound: true,
//     });

//     const dbSG = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Database',
//       allowAllOutbound: false,
//     });

//     // Add ingress rule for database access
//     dbSG.addIngressRule(
//       serverlessSG,
//       ec2.Port.tcp(5432),
//       'Allow PostgreSQL access from Lambda functions'
//     );

//     // Import shared resources
//     const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//       this,
//       'SharedPythonLayer',
//       cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn'))
//     );

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(
//       this,
//       'ImportedTextExtractorQueue',
//       {
//         queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//         queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//       }
//     );

//     // Create database construct
//     const database = new DatabaseConstruct(this, 'Database', {
//       vpc,
//       dbPassword: props.environmentConfig.httpPassword,
//       securityGroup: dbSG,
//       vpcSubnets: {
//         subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS
//       },
//     });

//     // Create API construct
//     const api = new ApiConstruct(this, 'Api', {
//       vpc,
//       securityGroup: serverlessSG,
//       environmentConfig: {
//         vpcId: props.environmentConfig.vpcId,
//         logLevel: props.environmentConfig.logLevel,
//         httpUser: props.environmentConfig.httpUser,
//         httpPassword: props.environmentConfig.httpPassword,
//         subnetIds: props.environmentConfig.subnetIds,
//       },
//       storageBucketName: storageBucket.bucketName,
//       queueUrl: textExtractorQueue.queueUrl,
//       lambdaConfig: props.lambdaConfig,
//       pythonLayer,
//       stageConfig,
//       vpcSubnets: {
//         subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS
//       },
//     });

//     // Create WAF construct
//     const waf = new WafConstruct(this, 'Waf', stageConfig);

//     // Create stack outputs
//     const outputs: Record<string, cdk.CfnOutputProps> = {
//       ApiHandlerArn: {
//         value: api.lambda.functionArn,
//         description: 'API Handler Lambda function ARN',
//         exportName: stageConfig.getResourceName('api-handler-arn'),
//       },
//       ApiHandlerName: {
//         value: api.lambda.functionName,
//         description: 'API Handler Lambda function name',
//         exportName: stageConfig.getResourceName('api-handler-name'),
//       },
//       ApiEndpoint: {
//         value: api.api.url,
//         description: 'API Gateway endpoint URL',
//         exportName: stageConfig.getResourceName('api-endpoint'),
//       },
//       ApiLogGroup: {
//         value: stageConfig.aws.apiGateway('api'),
//         description: 'API Gateway Log Group name',
//         exportName: stageConfig.getResourceName('api-log-group'),
//       },
//       LambdaLogGroup: {
//         value: stageConfig.aws.lambda('api-handler'),
//         description: 'Lambda Log Group name',
//         exportName: stageConfig.getResourceName('lambda-log-group'),
//       },
//       DatabaseEndpoint: {
//         value: database.dbCluster.clusterEndpoint.hostname,
//         description: 'Database cluster endpoint',
//         exportName: stageConfig.getResourceName('db-endpoint'),
//       },
//       StorageBucketName: {
//         value: storageBucket.bucketName,
//         description: 'Storage bucket name',
//         exportName: stageConfig.getResourceName('storage-bucket-name'),
//       }
//     };

//     Object.entries(outputs).forEach(([name, props]) => new cdk.CfnOutput(this, name, props));
//   }
// }
