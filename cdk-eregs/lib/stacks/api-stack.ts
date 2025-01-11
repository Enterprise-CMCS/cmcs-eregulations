import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_s3 as s3,
  aws_lambda as lambda,
  aws_sqs as sqs,
  aws_ssm as ssm,
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
    subnetIds: string[];
  };
}

export class APIStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
    super(scope, id, props);

    // Get all SSM parameters using valueForStringParameter
    const ssmParams = {
      dbPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/password'),
      dbHost: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/host'),
      dbPort: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port'),
      gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
      httpUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
      httpPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
      readerUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/reader_user'),
      readerPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/reader_password'),
      djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
      baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
      customUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url'),
      surveyUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/survey_url'),
      signupUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/signup_url'),
      demoVideoUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/demo_video_url'),
      oidcClientId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/client_id'),
      oidcClientSecret: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/client_secret'),
      oidcAuthEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/authorization_endpoint'),
      oidcTokenEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/token_endpoint'),
      oidcJwksEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/jwks_endpoint'),
      oidcUserEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/user_endpoint'),
      oidcEndEuaSession: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/end_eua_session'),
      basicSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/basic_search_filter'),
      quotedSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/quoted_search_filter'),
      searchHeadlineTextMax: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_text_max'),
      searchHeadlineMinWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_min_words'),
      searchHeadlineMaxWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_words'),
      searchHeadlineMaxFragments: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_fragments'),
      euaFeatureFlag: ssm.StringParameter.valueForStringParameter(this, '/eregulations/eua/featureflag'),
    };

    // Create storage bucket with same naming as serverless
    const storageBucket = new s3.Bucket(this, 'StorageBucket', {
      bucketName: stageConfig.getResourceName(`file-repo-eregs`),
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

    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId,
    });

    const selectedSubnets: ec2.SubnetSelection = {
      subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
        ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
      ),
    };

    // Security groups
    const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions',
      allowAllOutbound: true,
    });

    const dbSG = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Database',
      allowAllOutbound: false,
    });

    dbSG.addIngressRule(
      serverlessSG,
      ec2.Port.tcp(5432),
      'Allow PostgreSQL access from Lambda functions',
    );

    // Import shared resources
    const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
      this,
      'SharedPythonLayer',
      cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn')),
    );

    const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
      queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
      queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
    });

    // Create database with SSM parameters
    const database = new DatabaseConstruct(this, 'Database', {
      vpc,
      dbPassword: ssmParams.dbPassword,
      securityGroup: dbSG,
      vpcSubnets: selectedSubnets,
    });

    // Environment variables matching serverless.yml exactly
    const environmentVariables = {
      DB_NAME: 'eregs',
      DB_USER: 'eregsuser',
      DB_PASSWORD: ssmParams.dbPassword,
      DB_HOST: ssmParams.dbHost,
      DB_PORT: ssmParams.dbPort,
      GA_ID: ssmParams.gaId,
      HTTP_AUTH_USER: ssmParams.httpUser,
      HTTP_AUTH_PASSWORD: ssmParams.httpPassword,
      DJANGO_USERNAME: ssmParams.readerUser,
      DJANGO_PASSWORD: ssmParams.readerPassword,
      DJANGO_ADMIN_USERNAME: ssmParams.httpUser,
      DJANGO_ADMIN_PASSWORD: ssmParams.httpPassword,
      DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
      ALLOWED_HOST: '.amazonaws.com',
      STAGE_ENV: stageConfig.environment,
      BASE_URL: ssmParams.baseUrl,
      CUSTOM_URL: ssmParams.customUrl,
      SURVEY_URL: ssmParams.surveyUrl,
      SIGNUP_URL: ssmParams.signupUrl,
      DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
      OIDC_RP_CLIENT_ID: ssmParams.oidcClientId,
      OIDC_RP_CLIENT_SECRET: ssmParams.oidcClientSecret,
      OIDC_OP_AUTHORIZATION_ENDPOINT: ssmParams.oidcAuthEndpoint,
      OIDC_OP_TOKEN_ENDPOINT: ssmParams.oidcTokenEndpoint,
      OIDC_OP_JWKS_ENDPOINT: ssmParams.oidcJwksEndpoint,
      OIDC_OP_USER_ENDPOINT: ssmParams.oidcUserEndpoint,
      OIDC_END_EUA_SESSION: ssmParams.oidcEndEuaSession,
      BASIC_SEARCH_FILTER: ssmParams.basicSearchFilter,
      QUOTED_SEARCH_FILTER: ssmParams.quotedSearchFilter,
      SEARCH_HEADLINE_TEXT_MAX: ssmParams.searchHeadlineTextMax,
      SEARCH_HEADLINE_MIN_WORDS: ssmParams.searchHeadlineMinWords,
      SEARCH_HEADLINE_MAX_WORDS: ssmParams.searchHeadlineMaxWords,
      SEARCH_HEADLINE_MAX_FRAGMENTS: ssmParams.searchHeadlineMaxFragments,
      EUA_FEATUREFLAG: ssmParams.euaFeatureFlag,
      AWS_STORAGE_BUCKET_NAME: storageBucket.bucketName,
      TEXT_EXTRACTOR_QUEUE_URL: textExtractorQueue.queueUrl,
      DEPLOY_NUMBER: process.env.RUN_ID || '',
    };

    // Create API with environment variables
    const api = new ApiConstruct(this, 'Api', {
      vpc,
      securityGroup: serverlessSG,
      environmentVariables,
      storageBucketName: storageBucket.bucketName,
      queueUrl: textExtractorQueue.queueUrl,
      lambdaConfig: props.lambdaConfig,
      pythonLayer,
      stageConfig,
      vpcSubnets: selectedSubnets,
    });

    // Grant permissions
    storageBucket.grantReadWrite(api.lambda);
    textExtractorQueue.grantSendMessages(api.lambda);

    // Create WAF
    const waf = new WafConstruct(this, 'Waf', stageConfig);

    // Stack outputs matching serverless.yml
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
//     subnetIds: string[];  // [privateSubnetAId, privateSubnetBId]
//   };
// }

// export class APIStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     // Create storage bucket
//     const storageBucket = new s3.Bucket(this, 'StorageBucket', {
//       bucketName: stageConfig.getResourceName(`file-repo-eregs`),
//       encryption: s3.BucketEncryption.S3_MANAGED,
//       blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
//       enforceSSL: true,
//       cors: [
//         {
//           allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
//           allowedOrigins: ['*'],
//           allowedHeaders: ['*'],
//           maxAge: 3000,
//         },
//       ],
//     });

//     // Look up VPC by ID
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     // Convert your array of subnet IDs into a SubnetSelection
//     // so we can actually deploy resources into those subnets.
//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
//         ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
//       ),
//     };

//     // Security group for Lambda / API
//     // (Adjust egress rules if you want to restrict external calls further)
//     const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Serverless Functions (Lambda/API)',
//       allowAllOutbound: true,
//     });

//     // Security group for Database
//     // (We set outbound to false to reduce exfil risk from the DB side)
//     const dbSG = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Aurora Database',
//       allowAllOutbound: false,
//     });

//     // Allow inbound PostgreSQL from the Lambda SG only
//     dbSG.addIngressRule(
//       serverlessSG,
//       ec2.Port.tcp(5432),
//       'Allow PostgreSQL access from Lambda functions',
//     );

//     // Import external resources
//     const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//       this,
//       'SharedPythonLayer',
//       cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn')),
//     );

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//     // Create the Database in the private subnets
//     const database = new DatabaseConstruct(this, 'Database', {
//       vpc,
//       dbPassword: props.environmentConfig.httpPassword,
//       securityGroup: dbSG,
//       // Pass our SubnetSelection
//       vpcSubnets: selectedSubnets,
//     });

//     // Create the API (Lambda + API Gateway) also in the private subnets
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
//       // Same subnets for the API’s Lambda
//       vpcSubnets: selectedSubnets,
//     });

//     // Create the WAF
//     const waf = new WafConstruct(this, 'Waf', stageConfig);

//     // Stack outputs
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
//       },
//     };

//     Object.entries(outputs).forEach(([name, config]) => new cdk.CfnOutput(this, name, config));
//   }
// }

