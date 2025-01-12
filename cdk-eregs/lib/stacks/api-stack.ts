import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_s3 as s3,
  aws_lambda as lambda,
  aws_sqs as sqs,
  aws_ssm as ssm,
  aws_logs as logs,
  aws_iam as iam,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import { ApiConstruct } from '../constructs/api-construct';
import { WafConstruct } from '../constructs/waf-construct';
import * as path from 'path';

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

    // Get SSM parameters
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

    // Create S3 Bucket
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

    // VPC Configuration
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId,
    });

    const selectedSubnets: ec2.SubnetSelection = {
      subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
        ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
      ),
    };

    // Security Group
    const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions',
      allowAllOutbound: true,
    });

    // Import Shared Resources
    const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
      this,
      'SharedPythonLayer',
      cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn')),
    );

    const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
      queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
      queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
    });

    // Common Environment Variables
    const environmentVariables = {
      STATIC_URL: `https://${stageConfig.getResourceName('static-assets')}.s3.amazonaws.com/`,
      WORKING_DIR: '/var/task',
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

    // Common Lambda Configuration
    const commonLambdaProps = {
      runtime: lambda.Runtime.PYTHON_3_12,
      vpc,
      vpcSubnets: selectedSubnets,
      securityGroups: [serverlessSG],
      layers: [pythonLayer],
      environment: environmentVariables,
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend')),
    };

    // Create Log Groups
    const createLogGroup = (name: string) => new logs.LogGroup(this, `${name}LogGroup`, {
      logGroupName: stageConfig.aws.lambda(name),
      retention: logs.RetentionDays.ONE_MONTH,
    });

    // Create Lambda Functions
    const regSiteLambda = new lambda.Function(this, 'RegSiteLambda', {
      ...commonLambdaProps,
      functionName: stageConfig.getResourceName('reg-site'),
      handler: 'handler.lambda_handler',
      timeout: cdk.Duration.seconds(30),
      memorySize: props.lambdaConfig.memorySize,
      logGroup: createLogGroup('reg-site'),
    });

    const migrateLambda = new lambda.Function(this, 'MigrateLambda', {
      ...commonLambdaProps,
      functionName: stageConfig.getResourceName('reg-core-migrate'),
      handler: 'migrate.handler',
      timeout: cdk.Duration.seconds(900),
      memorySize: 1024,
      logGroup: createLogGroup('reg-core-migrate'),
    });

    const createDbLambda = new lambda.Function(this, 'CreateDbLambda', {
      ...commonLambdaProps,
      functionName: stageConfig.getResourceName('createdb'),
      handler: 'createdb.handler',
      timeout: cdk.Duration.seconds(300),
      memorySize: 1024,
      logGroup: createLogGroup('createdb'),
    });

    const dropDbLambda = new lambda.Function(this, 'DropDbLambda', {
      ...commonLambdaProps,
      functionName: stageConfig.getResourceName('dropdb'),
      handler: 'dropdb.handler',
      timeout: cdk.Duration.seconds(300),
      memorySize: 1024,
      logGroup: createLogGroup('dropdb'),
    });

    const emptyBucketLambda = new lambda.Function(this, 'EmptyBucketLambda', {
      ...commonLambdaProps,
      functionName: stageConfig.getResourceName('empty-bucket'),
      handler: 'empty_bucket.handler',
      timeout: cdk.Duration.seconds(900),
      memorySize: 1024,
      logGroup: createLogGroup('empty-bucket'),
    });

    const createSuLambda = new lambda.Function(this, 'CreateSuLambda', {
      ...commonLambdaProps,
      functionName: stageConfig.getResourceName('create-su'),
      handler: 'createsu.handler',
      timeout: cdk.Duration.seconds(300),
      memorySize: 1024,
      logGroup: createLogGroup('create-su'),
    });

    // Create API Gateway
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
      lambda: regSiteLambda,
    });

    // Grant S3 Permissions
    storageBucket.grantReadWrite(regSiteLambda);
    storageBucket.grantReadWrite(emptyBucketLambda);

    // Grant SQS Permissions
    textExtractorQueue.grantSendMessages(regSiteLambda);

    // Create WAF
    const waf = new WafConstruct(this, 'Waf', stageConfig);

    // Create Stack Outputs
    const outputs: Record<string, cdk.CfnOutputProps> = {
      ApiHandlerArn: {
        value: regSiteLambda.functionArn,
        description: 'API Handler Lambda function ARN',
        exportName: stageConfig.getResourceName('api-handler-arn'),
      },
      ApiHandlerName: {
        value: regSiteLambda.functionName,
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
      StorageBucketName: {
        value: storageBucket.bucketName,
        description: 'Storage bucket name',
        exportName: stageConfig.getResourceName('storage-bucket-name'),
      },
    };

    // Add Lambda Output ARNs
    const lambdaOutputs = {
      CreateDbLambdaArn: createDbLambda.functionArn,
      MigrateLambdaArn: migrateLambda.functionArn,
      CreateSuLambdaArn: createSuLambda.functionArn,
      DropDbLambdaArn: dropDbLambda.functionArn,
      EmptyBucketLambdaArn: emptyBucketLambda.functionArn,
    };

    Object.entries(lambdaOutputs).forEach(([name, value]) => {
      outputs[name] = {
        value,
        description: `${name} Lambda function ARN`,
        exportName: stageConfig.getResourceName(name.toLowerCase()),
      };
    });

    // Create all outputs
    Object.entries(outputs).forEach(([name, config]) => 
      new cdk.CfnOutput(this, name, config)
    );

    // Add Lambda function permissions for database operations
    const dbLambdas = [
      createDbLambda,
      dropDbLambda,
      migrateLambda,
      createSuLambda,
    ];

    dbLambdas.forEach(lambdaFn => {
      lambdaFn.addToRolePolicy(new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          'rds:DescribeDBInstances',
          'rds:DescribeDBClusters',
        ],
        resources: ['*'],
      }));
    });

    // Add tags to all Lambda functions
    const allLambdas = [
      regSiteLambda,
      migrateLambda,
      createDbLambda,
      dropDbLambda,
      emptyBucketLambda,
      createSuLambda,
    ];

    const commonTags = {
      Environment: stageConfig.environment,
      Service: 'eregs',
      DeployedBy: 'CDK',
    };

    allLambdas.forEach(lambdaFn => {
      Object.entries(commonTags).forEach(([key, value]) => {
        cdk.Tags.of(lambdaFn).add(key, value);
      });
    });
  }
}


// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_s3 as s3,
//   aws_lambda as lambda,
//   aws_sqs as sqs,
//   aws_ssm as ssm,
//   aws_logs as logs,
//   aws_iam as iam,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';
// import { DatabaseConstruct } from '../constructs/database-construct';
// import { ApiConstruct } from '../constructs/api-construct';
// import { WafConstruct } from '../constructs/waf-construct';
// import * as path from 'path';

// interface APIStackProps extends cdk.StackProps {
//   lambdaConfig: {
//     memorySize: number;
//     timeout: number;
//     reservedConcurrentExecutions?: number;
//   };
//   environmentConfig: {
//     vpcId: string;
//     logLevel: string;
//     subnetIds: string[];
//   };
// }

// export class APIStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     // Get all SSM parameters using valueForStringParameter
//     const ssmParams = {
//       dbPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/password'),
//       dbHost: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/host'),
//       dbPort: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port'),
//       gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
//       httpUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
//       httpPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
//       readerUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/reader_user'),
//       readerPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/reader_password'),
//       djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
//       baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
//       customUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url'),
//       surveyUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/survey_url'),
//       signupUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/signup_url'),
//       demoVideoUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/demo_video_url'),
//       oidcClientId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/client_id'),
//       oidcClientSecret: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/client_secret'),
//       oidcAuthEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/authorization_endpoint'),
//       oidcTokenEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/token_endpoint'),
//       oidcJwksEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/jwks_endpoint'),
//       oidcUserEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/user_endpoint'),
//       oidcEndEuaSession: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/end_eua_session'),
//       basicSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/basic_search_filter'),
//       quotedSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/quoted_search_filter'),
//       searchHeadlineTextMax: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_text_max'),
//       searchHeadlineMinWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_min_words'),
//       searchHeadlineMaxWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_words'),
//       searchHeadlineMaxFragments: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_fragments'),
//       euaFeatureFlag: ssm.StringParameter.valueForStringParameter(this, '/eregulations/eua/featureflag'),
//     };

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

//     // VPC configuration
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
//         ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
//       ),
//     };

//     // Security groups
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

//     dbSG.addIngressRule(
//       serverlessSG,
//       ec2.Port.tcp(5432),
//       'Allow PostgreSQL access from Lambda functions',
//     );

//     // Import shared resources
//     const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//       this,
//       'SharedPythonLayer',
//       cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn')),
//     );

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//     // Create log groups
//     const migrateLambdaLogGroup = new logs.LogGroup(this, 'MigrateLambdaLogGroup', {
//       logGroupName: stageConfig.aws.lambda('reg-core-migrate'),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

//     const authorizeLambdaLogGroup = new logs.LogGroup(this, 'AuthorizeLambdaLogGroup', {
//       logGroupName: stageConfig.aws.lambda('reg-authorizer'),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

//     const createSuLambdaLogGroup = new logs.LogGroup(this, 'CreateSuLambdaLogGroup', {
//       logGroupName: stageConfig.aws.lambda('create-su'),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

//     // Create database
//     const database = new DatabaseConstruct(this, 'Database', {
//       vpc,
//       dbPassword: ssmParams.dbPassword,
//       securityGroup: dbSG,
//       vpcSubnets: selectedSubnets,
//     });

//     // Environment variables
//     const environmentVariables = {
//       DB_NAME: 'eregs',
//       DB_USER: 'eregsuser',
//       DB_PASSWORD: ssmParams.dbPassword,
//       DB_HOST: ssmParams.dbHost,
//       DB_PORT: ssmParams.dbPort,
//       GA_ID: ssmParams.gaId,
//       HTTP_AUTH_USER: ssmParams.httpUser,
//       HTTP_AUTH_PASSWORD: ssmParams.httpPassword,
//       DJANGO_USERNAME: ssmParams.readerUser,
//       DJANGO_PASSWORD: ssmParams.readerPassword,
//       DJANGO_ADMIN_USERNAME: ssmParams.httpUser,
//       DJANGO_ADMIN_PASSWORD: ssmParams.httpPassword,
//       DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
//       ALLOWED_HOST: '.amazonaws.com',
//       STAGE_ENV: stageConfig.environment,
//       BASE_URL: ssmParams.baseUrl,
//       CUSTOM_URL: ssmParams.customUrl,
//       SURVEY_URL: ssmParams.surveyUrl,
//       SIGNUP_URL: ssmParams.signupUrl,
//       DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
//       OIDC_RP_CLIENT_ID: ssmParams.oidcClientId,
//       OIDC_RP_CLIENT_SECRET: ssmParams.oidcClientSecret,
//       OIDC_OP_AUTHORIZATION_ENDPOINT: ssmParams.oidcAuthEndpoint,
//       OIDC_OP_TOKEN_ENDPOINT: ssmParams.oidcTokenEndpoint,
//       OIDC_OP_JWKS_ENDPOINT: ssmParams.oidcJwksEndpoint,
//       OIDC_OP_USER_ENDPOINT: ssmParams.oidcUserEndpoint,
//       OIDC_END_EUA_SESSION: ssmParams.oidcEndEuaSession,
//       BASIC_SEARCH_FILTER: ssmParams.basicSearchFilter,
//       QUOTED_SEARCH_FILTER: ssmParams.quotedSearchFilter,
//       SEARCH_HEADLINE_TEXT_MAX: ssmParams.searchHeadlineTextMax,
//       SEARCH_HEADLINE_MIN_WORDS: ssmParams.searchHeadlineMinWords,
//       SEARCH_HEADLINE_MAX_WORDS: ssmParams.searchHeadlineMaxWords,
//       SEARCH_HEADLINE_MAX_FRAGMENTS: ssmParams.searchHeadlineMaxFragments,
//       EUA_FEATUREFLAG: ssmParams.euaFeatureFlag,
//       AWS_STORAGE_BUCKET_NAME: storageBucket.bucketName,
//       TEXT_EXTRACTOR_QUEUE_URL: textExtractorQueue.queueUrl,
//       DEPLOY_NUMBER: process.env.RUN_ID || '',
//     };

//     // Common Lambda configuration
//     const commonLambdaProps = {
//       runtime: lambda.Runtime.PYTHON_3_12,
//       vpc,
//       vpcSubnets: selectedSubnets,
//       securityGroups: [serverlessSG],
//       layers: [pythonLayer],
//       environment: environmentVariables,
//     };

//     // Create the main API
//     const api = new ApiConstruct(this, 'Api', {
//       vpc,
//       securityGroup: serverlessSG,
//       environmentVariables,
//       storageBucketName: storageBucket.bucketName,
//       queueUrl: textExtractorQueue.queueUrl,
//       lambdaConfig: props.lambdaConfig,
//       pythonLayer,
//       stageConfig,
//       vpcSubnets: selectedSubnets,
//     });

//     // Create Migration Lambda
//     const migrateLambda = new lambda.Function(this, 'MigrateLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('reg-core-migrate'),
//       handler: 'migrate.handler',
//       timeout: cdk.Duration.seconds(900),
//       memorySize: 1024,
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend')),
//       logGroup: migrateLambdaLogGroup,
//     });

//     // Create Authorize Lambda
//     const authorizeLambda = new lambda.Function(this, 'AuthorizeLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('reg-authorizer'),
//       handler: 'authorizer.handler',
//       timeout: cdk.Duration.seconds(30),
//       memorySize: 128,
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend')),
//       logGroup: authorizeLambdaLogGroup,
//     });

//     // Create CreateSU Lambda
//     const createSuLambda = new lambda.Function(this, 'CreateSuLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('create-su'),
//       handler: 'createsu.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend')),
//       logGroup: createSuLambdaLogGroup,
//     });

//     // Grant permissions
//     storageBucket.grantReadWrite(api.lambda);
//     textExtractorQueue.grantSendMessages(api.lambda);

//     // Grant database access
//     [migrateLambda, createSuLambda].forEach(lambda => {
//       lambda.addToRolePolicy(new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: [
//           'rds:DescribeDBInstances',
//           'rds:DescribeDBClusters',
//         ],
//         resources: [database.dbCluster.clusterArn],
//       }));
//     });

//     // Grant SSM access to authorizer
//     authorizeLambda.addToRolePolicy(new iam.PolicyStatement({
//       effect: iam.Effect.ALLOW,
//       actions: [
//         'ssm:GetParameter',
//         'ssm:GetParameters',
//       ],
//       resources: [
//         `arn:aws:ssm:${this.region}:${this.account}:parameter/eregulations/http/*`,
//       ],
//     }));

//     // Create WAF
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
//       MigrateLambdaArn: {
//         value: migrateLambda.functionArn,
//         description: 'Migration Lambda function ARN',
//         exportName: stageConfig.getResourceName('migrate-lambda-arn'),
//       },
//       MigrateLambdaName: {
//         value: migrateLambda.functionName,
//         description: 'Migration Lambda function name',
//         exportName: stageConfig.getResourceName('migrate-lambda-name'),
//       },
//       AuthorizeLambdaArn: {
//         value: authorizeLambda.functionArn,
//         description: 'Authorize Lambda function ARN',
//         exportName: stageConfig.getResourceName('authorize-lambda-arn'),
//       },
//       AuthorizeLambdaName: {
//         value: authorizeLambda.functionName,
//         description: 'Authorize Lambda function name',
//         exportName: stageConfig.getResourceName('authorize-lambda-name'),
//       },
//       CreateSuLambdaArn: {
//         value: createSuLambda.functionArn,
//         description: 'Create Superuser Lambda function ARN',
//         exportName: stageConfig.getResourceName('create-su-lambda-arn'),
//       },
//       CreateSuLambdaName: {
//         value: createSuLambda.functionName,
//         description: 'Create Superuser Lambda function name',
//         exportName: stageConfig.getResourceName('create-su-lambda-name'),
//       },
//     };

//     Object.entries(outputs).forEach(([name, config]) => new cdk.CfnOutput(this, name, config));

//     // Add tags
//     const commonTags = {
//       Environment: stageConfig.environment,
//       Service: 'eregs',
//       DeployedBy: 'CDK',
//     };

//     [api.lambda, migrateLambda, authorizeLambda, createSuLambda].forEach(lambdaFn => {
//       Object.entries(commonTags).forEach(([key, value]) => {
//         cdk.Tags.of(lambdaFn).add(key, value);
//       });
//     });
//   }
// }


// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_s3 as s3,
//   aws_lambda as lambda,
//   aws_sqs as sqs,
//   aws_ssm as ssm,
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
//     subnetIds: string[];
//   };
// }

// export class APIStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     // Get all SSM parameters using valueForStringParameter
//     const ssmParams = {
//       dbPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/password'),
//       dbHost: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/host'),
//       dbPort: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port'),
//       gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
//       httpUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
//       httpPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
//       readerUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/reader_user'),
//       readerPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/reader_password'),
//       djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
//       baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
//       customUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url'),
//       surveyUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/survey_url'),
//       signupUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/signup_url'),
//       demoVideoUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/demo_video_url'),
//       oidcClientId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/client_id'),
//       oidcClientSecret: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/client_secret'),
//       oidcAuthEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/authorization_endpoint'),
//       oidcTokenEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/token_endpoint'),
//       oidcJwksEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/jwks_endpoint'),
//       oidcUserEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/user_endpoint'),
//       oidcEndEuaSession: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/end_eua_session'),
//       basicSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/basic_search_filter'),
//       quotedSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/quoted_search_filter'),
//       searchHeadlineTextMax: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_text_max'),
//       searchHeadlineMinWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_min_words'),
//       searchHeadlineMaxWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_words'),
//       searchHeadlineMaxFragments: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_fragments'),
//       euaFeatureFlag: ssm.StringParameter.valueForStringParameter(this, '/eregulations/eua/featureflag'),
//     };

//     // Create storage bucket with same naming as serverless
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

//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
//         ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
//       ),
//     };

//     // Security groups
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

//     dbSG.addIngressRule(
//       serverlessSG,
//       ec2.Port.tcp(5432),
//       'Allow PostgreSQL access from Lambda functions',
//     );

//     // Import shared resources
//     const pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//       this,
//       'SharedPythonLayer',
//       cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn')),
//     );

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//     // Create database with SSM parameters
//     const database = new DatabaseConstruct(this, 'Database', {
//       vpc,
//       dbPassword: ssmParams.dbPassword,
//       securityGroup: dbSG,
//       vpcSubnets: selectedSubnets,
//     });

//     // Environment variables matching serverless.yml exactly
//     const environmentVariables = {
//       DB_NAME: 'eregs',
//       DB_USER: 'eregsuser',
//       DB_PASSWORD: ssmParams.dbPassword,
//       DB_HOST: ssmParams.dbHost,
//       DB_PORT: ssmParams.dbPort,
//       GA_ID: ssmParams.gaId,
//       HTTP_AUTH_USER: ssmParams.httpUser,
//       HTTP_AUTH_PASSWORD: ssmParams.httpPassword,
//       DJANGO_USERNAME: ssmParams.readerUser,
//       DJANGO_PASSWORD: ssmParams.readerPassword,
//       DJANGO_ADMIN_USERNAME: ssmParams.httpUser,
//       DJANGO_ADMIN_PASSWORD: ssmParams.httpPassword,
//       DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
//       ALLOWED_HOST: '.amazonaws.com',
//       STAGE_ENV: stageConfig.environment,
//       BASE_URL: ssmParams.baseUrl,
//       CUSTOM_URL: ssmParams.customUrl,
//       SURVEY_URL: ssmParams.surveyUrl,
//       SIGNUP_URL: ssmParams.signupUrl,
//       DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
//       OIDC_RP_CLIENT_ID: ssmParams.oidcClientId,
//       OIDC_RP_CLIENT_SECRET: ssmParams.oidcClientSecret,
//       OIDC_OP_AUTHORIZATION_ENDPOINT: ssmParams.oidcAuthEndpoint,
//       OIDC_OP_TOKEN_ENDPOINT: ssmParams.oidcTokenEndpoint,
//       OIDC_OP_JWKS_ENDPOINT: ssmParams.oidcJwksEndpoint,
//       OIDC_OP_USER_ENDPOINT: ssmParams.oidcUserEndpoint,
//       OIDC_END_EUA_SESSION: ssmParams.oidcEndEuaSession,
//       BASIC_SEARCH_FILTER: ssmParams.basicSearchFilter,
//       QUOTED_SEARCH_FILTER: ssmParams.quotedSearchFilter,
//       SEARCH_HEADLINE_TEXT_MAX: ssmParams.searchHeadlineTextMax,
//       SEARCH_HEADLINE_MIN_WORDS: ssmParams.searchHeadlineMinWords,
//       SEARCH_HEADLINE_MAX_WORDS: ssmParams.searchHeadlineMaxWords,
//       SEARCH_HEADLINE_MAX_FRAGMENTS: ssmParams.searchHeadlineMaxFragments,
//       EUA_FEATUREFLAG: ssmParams.euaFeatureFlag,
//       AWS_STORAGE_BUCKET_NAME: storageBucket.bucketName,
//       TEXT_EXTRACTOR_QUEUE_URL: textExtractorQueue.queueUrl,
//       DEPLOY_NUMBER: process.env.RUN_ID || '',
//     };

//     // Create API with environment variables
//     const api = new ApiConstruct(this, 'Api', {
//       vpc,
//       securityGroup: serverlessSG,
//       environmentVariables,
//       storageBucketName: storageBucket.bucketName,
//       queueUrl: textExtractorQueue.queueUrl,
//       lambdaConfig: props.lambdaConfig,
//       pythonLayer,
//       stageConfig,
//       vpcSubnets: selectedSubnets,
//     });

//     // Grant permissions
//     storageBucket.grantReadWrite(api.lambda);
//     textExtractorQueue.grantSendMessages(api.lambda);

//     // Create WAF
//     const waf = new WafConstruct(this, 'Waf', stageConfig);

//     // Stack outputs matching serverless.yml
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


