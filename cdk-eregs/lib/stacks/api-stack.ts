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

    // For non-sensitive parameters, use valueForStringParameter
    const ssmParams = {
      dbHost: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/host'),
      dbPort: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port'),
      gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
      djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
      baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
      customUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url'),
      surveyUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/survey_url'),
      signupUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/signup_url'),
      demoVideoUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/demo_video_url'),
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

    // For sensitive parameters
    const sensitiveParams = {
      dbPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'DbPassword', {
        parameterName: '/eregulations/db/password',
        version: 1,
      }).parameterName,
      httpUser: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'HttpUser', {
        parameterName: '/eregulations/http/user',
        version: 1,
      }).parameterName,
      httpPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'HttpPassword', {
        parameterName: '/eregulations/http/password',
        version: 1,
      }).parameterName,
      readerUser: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ReaderUser', {
        parameterName: '/eregulations/http/reader_user',
        version: 1,
      }).parameterName,
      readerPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ReaderPassword', {
        parameterName: '/eregulations/http/reader_password',
        version: 1,
      }).parameterName,
      oidcClientId: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'OidcClientId', {
        parameterName: '/eregulations/oidc/client_id',
        version: 1,
      }).parameterName,
      oidcClientSecret: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'OidcClientSecret', {
        parameterName: '/eregulations/oidc/client_secret',
        version: 1,
      }).parameterName,
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
      subnets: [
        ec2.Subnet.fromSubnetId(this, 'PrivateSubnet', props.environmentConfig.subnetIds[0])
      ],
    };

    // Security Group
    const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions',
      allowAllOutbound: true,
    });

    const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
      queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
      queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
    });

    // Environment variables
    const environmentVariables = {
      DB_NAME: 'eregs',
      DB_USER: 'eregsuser',
      DB_PASSWORD: `\${SSM:${sensitiveParams.dbPassword}}`,
      DB_HOST: ssmParams.dbHost,
      DB_PORT: ssmParams.dbPort,
      GA_ID: ssmParams.gaId,
      HTTP_AUTH_USER: `\${SSM:${sensitiveParams.httpUser}}`,
      HTTP_AUTH_PASSWORD: `\${SSM:${sensitiveParams.httpPassword}}`,
      DJANGO_USERNAME: `\${SSM:${sensitiveParams.readerUser}}`,
      DJANGO_PASSWORD: `\${SSM:${sensitiveParams.readerPassword}}`,
      DJANGO_ADMIN_USERNAME: `\${SSM:${sensitiveParams.httpUser}}`,
      DJANGO_ADMIN_PASSWORD: `\${SSM:${sensitiveParams.httpPassword}}`,
      DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
      ALLOWED_HOST: '.amazonaws.com',
      STAGE_ENV: stageConfig.environment,
      STATIC_URL: `https://${stageConfig.getResourceName('static-assets')}.s3.amazonaws.com/`,
      WORKING_DIR: '/var/task',
      BASE_URL: ssmParams.baseUrl,
      CUSTOM_URL: ssmParams.customUrl,
      SURVEY_URL: ssmParams.surveyUrl,
      SIGNUP_URL: ssmParams.signupUrl,
      DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
      OIDC_RP_CLIENT_ID: `\${SSM:${sensitiveParams.oidcClientId}}`,
      OIDC_RP_CLIENT_SECRET: `\${SSM:${sensitiveParams.oidcClientSecret}}`,
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
      AWS_STORAGE_BUCKET_NAME: stageConfig.getResourceName(`file-repo-eregs`),
      TEXT_EXTRACTOR_QUEUE_URL: textExtractorQueue.queueUrl,
      DEPLOY_NUMBER: process.env.RUN_ID || '',
    };

    // Create Log Groups
    const createLogGroup = (name: string) => new logs.LogGroup(this, `${name}LogGroup`, {
      logGroupName: stageConfig.aws.lambda(name),
      retention: logs.RetentionDays.ONE_MONTH,
    });

    // Create Docker Lambda Functions
    const createDockerLambda = (name: string, dockerFile: string, handler: string, timeout: number = 300) => {
      return new lambda.DockerImageFunction(this, `${name}Lambda`, {
        functionName: stageConfig.getResourceName(name.toLowerCase()),
        code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/backend'), {
          file: dockerFile,
          cmd: [handler]
        }),
        vpc,
        vpcSubnets: selectedSubnets,
        securityGroups: [serverlessSG],
        timeout: cdk.Duration.seconds(timeout),
        memorySize: props.lambdaConfig.memorySize,
        environment: environmentVariables,
        logGroup: createLogGroup(name.toLowerCase())
      });
    };

    // RegSite Lambda
    const regSiteLambda = createDockerLambda('RegSite', 'regsite.Dockerfile', 'handler.lambda_handler', 30);

    // Other Lambda functions
    const migrateLambda = createDockerLambda('Migrate', 'migrate.Dockerfile', 'migrate.handler', 900);
    const createDbLambda = createDockerLambda('CreateDb', 'createdb.Dockerfile', 'createdb.handler');
    const dropDbLambda = createDockerLambda('DropDb', 'dropdb.Dockerfile', 'dropdb.handler');
    const emptyBucketLambda = createDockerLambda('EmptyBucket', 'empty_bucket.Dockerfile', 'empty_bucket.handler', 900);
    const createSuLambda = createDockerLambda('CreateSu', 'createsu.Dockerfile', 'createsu.handler');

    // Create API Gateway
    const api = new ApiConstruct(this, 'Api', {
      vpc,
      securityGroup: serverlessSG,
      environmentVariables,
      storageBucketName: storageBucket.bucketName,
      queueUrl: textExtractorQueue.queueUrl,
      lambdaConfig: props.lambdaConfig,
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

//     // For non-sensitive parameters, use valueForStringParameter
//     const ssmParams = {
//       dbHost: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/host'),
//       dbPort: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port'),
//       gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
//       djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
//       baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
//       customUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url'),
//       surveyUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/survey_url'),
//       signupUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/signup_url'),
//       demoVideoUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/demo_video_url'),
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

//     // For sensitive parameters
//     const sensitiveParams = {
//       dbPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'DbPassword', {
//         parameterName: '/eregulations/db/password',
//         version: 1,
//       }).parameterName,
//       httpUser: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'HttpUser', {
//         parameterName: '/eregulations/http/user',
//         version: 1,
//       }).parameterName,
//       httpPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'HttpPassword', {
//         parameterName: '/eregulations/http/password',
//         version: 1,
//       }).parameterName,
//       readerUser: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ReaderUser', {
//         parameterName: '/eregulations/http/reader_user',
//         version: 1,
//       }).parameterName,
//       readerPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ReaderPassword', {
//         parameterName: '/eregulations/http/reader_password',
//         version: 1,
//       }).parameterName,
//       oidcClientId: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'OidcClientId', {
//         parameterName: '/eregulations/oidc/client_id',
//         version: 1,
//       }).parameterName,
//       oidcClientSecret: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'OidcClientSecret', {
//         parameterName: '/eregulations/oidc/client_secret',
//         version: 1,
//       }).parameterName,
//     };

//     // Create S3 Bucket
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

//     // VPC Configuration
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: [
//         ec2.Subnet.fromSubnetId(this, 'PrivateSubnet', props.environmentConfig.subnetIds[0])
//       ],
//     };

//     // Security Group
//     const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Serverless Functions',
//       allowAllOutbound: true,
//     });

//     // Get Python Layer for non-Docker lambdas
//     let pythonLayer: lambda.ILayerVersion;
//     try {
//       const layerVersionId = cdk.Fn.importValue(
//         stageConfig.getResourceName('python-layer-version')
//       );
//       pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//         this,
//         'SharedPythonLayer',
//         cdk.Fn.importValue(`${stageConfig.getResourceName('python-layer-arn')}-${layerVersionId}`)
//       );
//     } catch (error) {
//       pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//         this,
//         'SharedPythonLayer',
//         cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn'))
//       );
//       console.warn('Using legacy layer reference. Please update StaticAssetsStack first.');
//     }

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//     // Environment variables
//     const environmentVariables = {
//       DB_NAME: 'eregs',
//       DB_USER: 'eregsuser',
//       DB_PASSWORD: `\${SSM:${sensitiveParams.dbPassword}}`,
//       DB_HOST: ssmParams.dbHost,
//       DB_PORT: ssmParams.dbPort,
//       GA_ID: ssmParams.gaId,
//       HTTP_AUTH_USER: `\${SSM:${sensitiveParams.httpUser}}`,
//       HTTP_AUTH_PASSWORD: `\${SSM:${sensitiveParams.httpPassword}}`,
//       DJANGO_USERNAME: `\${SSM:${sensitiveParams.readerUser}}`,
//       DJANGO_PASSWORD: `\${SSM:${sensitiveParams.readerPassword}}`,
//       DJANGO_ADMIN_USERNAME: `\${SSM:${sensitiveParams.httpUser}}`,
//       DJANGO_ADMIN_PASSWORD: `\${SSM:${sensitiveParams.httpPassword}}`,
//       DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
//       ALLOWED_HOST: '.amazonaws.com',
//       STAGE_ENV: stageConfig.environment,
//       STATIC_URL: `https://${stageConfig.getResourceName('static-assets')}.s3.amazonaws.com/`,
//       WORKING_DIR: '/var/task',
//       BASE_URL: ssmParams.baseUrl,
//       CUSTOM_URL: ssmParams.customUrl,
//       SURVEY_URL: ssmParams.surveyUrl,
//       SIGNUP_URL: ssmParams.signupUrl,
//       DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
//       OIDC_RP_CLIENT_ID: `\${SSM:${sensitiveParams.oidcClientId}}`,
//       OIDC_RP_CLIENT_SECRET: `\${SSM:${sensitiveParams.oidcClientSecret}}`,
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
//       AWS_STORAGE_BUCKET_NAME: stageConfig.getResourceName(`file-repo-eregs`),
//       TEXT_EXTRACTOR_QUEUE_URL: textExtractorQueue.queueUrl,
//       DEPLOY_NUMBER: process.env.RUN_ID || '',
//     };

//     // Create Log Groups
//     const createLogGroup = (name: string) => new logs.LogGroup(this, `${name}LogGroup`, {
//       logGroupName: stageConfig.aws.lambda(name),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

//     // RegSite Lambda with Docker
//     const regSiteLambda = new lambda.DockerImageFunction(this, 'RegSiteLambda', {
//       functionName: stageConfig.getResourceName('reg-site'),
//       code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/backend'), {
//         file: 'regsite.Dockerfile',
//         cmd: ['handler.lambda_handler']
//       }),
//       vpc,
//       vpcSubnets: selectedSubnets,
//       securityGroups: [serverlessSG],
//       timeout: cdk.Duration.seconds(30),
//       memorySize: props.lambdaConfig.memorySize,
//       environment: environmentVariables,
//       logGroup: createLogGroup('reg-site')
//     });

//     // Common Lambda Configuration for non-Docker lambdas
//     const commonLambdaProps = {
//       runtime: lambda.Runtime.PYTHON_3_12,
//       vpc,
//       vpcSubnets: selectedSubnets,
//       securityGroups: [serverlessSG],
//       layers: [pythonLayer],
//       environment: environmentVariables,
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend')),
//     };

//     // Other Lambda functions with layers
//     const migrateLambda = new lambda.Function(this, 'MigrateLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('reg-core-migrate'),
//       handler: 'migrate.handler',
//       timeout: cdk.Duration.seconds(900),
//       memorySize: 1024,
//       logGroup: createLogGroup('reg-core-migrate'),
//     });

//     const createDbLambda = new lambda.Function(this, 'CreateDbLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('createdb'),
//       handler: 'createdb.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       logGroup: createLogGroup('createdb'),
//     });

//     const dropDbLambda = new lambda.Function(this, 'DropDbLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('dropdb'),
//       handler: 'dropdb.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       logGroup: createLogGroup('dropdb'),
//     });

//     const emptyBucketLambda = new lambda.Function(this, 'EmptyBucketLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('empty-bucket'),
//       handler: 'empty_bucket.handler',
//       timeout: cdk.Duration.seconds(900),
//       memorySize: 1024,
//       logGroup: createLogGroup('empty-bucket'),
//     });

//     const createSuLambda = new lambda.Function(this, 'CreateSuLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('create-su'),
//       handler: 'createsu.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       logGroup: createLogGroup('create-su'),
//     });

//     // Create API Gateway
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
//       lambda: regSiteLambda,
//     });

//     // Grant S3 Permissions
//     storageBucket.grantReadWrite(regSiteLambda);
//     storageBucket.grantReadWrite(emptyBucketLambda);

//     // Grant SQS Permissions
//     textExtractorQueue.grantSendMessages(regSiteLambda);

//     // Create WAF
//     const waf = new WafConstruct(this, 'Waf', stageConfig);

//     // Create Stack Outputs
//     const outputs: Record<string, cdk.CfnOutputProps> = {
//       ApiHandlerArn: {
//         value: regSiteLambda.functionArn,
//         description: 'API Handler Lambda function ARN',
//         exportName: stageConfig.getResourceName('api-handler-arn'),
//       },
//       ApiHandlerName: {
//         value: regSiteLambda.functionName,
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
//       StorageBucketName: {
//         value: storageBucket.bucketName,
//         description: 'Storage bucket name',
//         exportName: stageConfig.getResourceName('storage-bucket-name'),
//       },
//     };

//     // Add Lambda Output ARNs
//     const lambdaOutputs = {
//       CreateDbLambdaArn: createDbLambda.functionArn,
//       MigrateLambdaArn: migrateLambda.functionArn,
//       CreateSuLambdaArn: createSuLambda.functionArn,
//       DropDbLambdaArn: dropDbLambda.functionArn,
//       EmptyBucketLambdaArn: emptyBucketLambda.functionArn,
//     };

//     Object.entries(lambdaOutputs).forEach(([name, value]) => {
//       outputs[name] = {
//         value,
//         description: `${name} Lambda function ARN`,
//         exportName: stageConfig.getResourceName(name.toLowerCase()),
//       };
//     });

//     // Create all outputs
//     Object.entries(outputs).forEach(([name, config]) => 
//       new cdk.CfnOutput(this, name, config)
//     );

//     // Add Lambda function permissions for database operations
//     const dbLambdas = [
//       createDbLambda,
//       dropDbLambda,
//       migrateLambda,
//       createSuLambda,
//     ];

//     dbLambdas.forEach(lambdaFn => {
//       lambdaFn.addToRolePolicy(new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: [
//           'rds:DescribeDBInstances',
//           'rds:DescribeDBClusters',
//         ],
//         resources: ['*'],
//       }));
//     });

//     // Add tags to all Lambda functions
//     const allLambdas = [
//       regSiteLambda,
//       migrateLambda,
//       createDbLambda,
//       dropDbLambda,
//       emptyBucketLambda,
//       createSuLambda,
//     ];

//     const commonTags = {
//       Environment: stageConfig.environment,
//       Service: 'eregs',
//       DeployedBy: 'CDK',
//     };

//     allLambdas.forEach(lambdaFn => {
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
//   aws_logs as logs,
//   aws_iam as iam,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';
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

//    // For non-sensitive parameters, use valueForStringParameter
// const ssmParams = {
//   dbHost: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/host'),
//   dbPort: ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port'),
//   gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
//   djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
//   baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
//   customUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url'),
//   surveyUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/survey_url'),
//   signupUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/signup_url'),
//   demoVideoUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/demo_video_url'),
//   oidcAuthEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/authorization_endpoint'),
//   oidcTokenEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/token_endpoint'),
//   oidcJwksEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/jwks_endpoint'),
//   oidcUserEndpoint: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/user_endpoint'),
//   oidcEndEuaSession: ssm.StringParameter.valueForStringParameter(this, '/eregulations/oidc/end_eua_session'),
//   basicSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/basic_search_filter'),
//   quotedSearchFilter: ssm.StringParameter.valueForStringParameter(this, '/eregulations/quoted_search_filter'),
//   searchHeadlineTextMax: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_text_max'),
//   searchHeadlineMinWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_min_words'),
//   searchHeadlineMaxWords: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_words'),
//   searchHeadlineMaxFragments: ssm.StringParameter.valueForStringParameter(this, '/eregulations/search_headline_max_fragments'),
//   euaFeatureFlag: ssm.StringParameter.valueForStringParameter(this, '/eregulations/eua/featureflag'),
// };

// // For sensitive parameters, use SecureString and reference them directly
// const sensitiveParams = {
//   dbPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'DbPassword', {
//     parameterName: '/eregulations/db/password',
//     version: 1,
//   }).parameterName,
//   httpUser: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'HttpUser', {
//     parameterName: '/eregulations/http/user',
//     version: 1,
//   }).parameterName,
//   httpPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'HttpPassword', {
//     parameterName: '/eregulations/http/password',
//     version: 1,
//   }).parameterName,
//   readerUser: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ReaderUser', {
//     parameterName: '/eregulations/http/reader_user',
//     version: 1,
//   }).parameterName,
//   readerPassword: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'ReaderPassword', {
//     parameterName: '/eregulations/http/reader_password',
//     version: 1,
//   }).parameterName,
//   oidcClientId: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'OidcClientId', {
//     parameterName: '/eregulations/oidc/client_id',
//     version: 1,
//   }).parameterName,
//   oidcClientSecret: ssm.StringParameter.fromSecureStringParameterAttributes(this, 'OidcClientSecret', {
//     parameterName: '/eregulations/oidc/client_secret',
//     version: 1,
//   }).parameterName,
// };

//     // Create S3 Bucket
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

//     // // VPC Configuration
//     // const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//     //   vpcId: props.environmentConfig.vpcId,
//     // });

//     // const selectedSubnets: ec2.SubnetSelection = {
//     //   subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
//     //     ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
//     //   ),
//     // };
//     // VPC Configuration
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: [
//         ec2.Subnet.fromSubnetId(this, 'PrivateSubnet', props.environmentConfig.subnetIds[0])
//       ],
//     };
//     // Security Group
//     const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Serverless Functions',
//       allowAllOutbound: true,
//     });
//     // Try to get the newest layer version, but fallback gracefully if not found
//     // First fix the layer import type and setup:
//     let pythonLayer: lambda.ILayerVersion;
//     try {
//       // Try to get the versioned layer first
//       const layerVersionId = cdk.Fn.importValue(
//         stageConfig.getResourceName('python-layer-version')
//       );
      
//       pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//         this,
//         'SharedPythonLayer',
//         cdk.Fn.importValue(`${stageConfig.getResourceName('python-layer-arn')}-${layerVersionId}`)
//       );
//     } catch (error) {
//       // Fall back to the legacy layer reference if versioned one is not found
//       pythonLayer = lambda.LayerVersion.fromLayerVersionArn(
//         this,
//         'SharedPythonLayer',
//         cdk.Fn.importValue(stageConfig.getResourceName('python-layer-arn'))
//       );
//       console.warn('Using legacy layer reference. Please update StaticAssetsStack first.');
//     }

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//    // Update the environment variables
// const environmentVariables = {
//   DB_NAME: 'eregs',
//   DB_USER: 'eregsuser',
//   DB_PASSWORD: `\${SSM:${sensitiveParams.dbPassword}}`,
//   DB_HOST: ssmParams.dbHost,
//   DB_PORT: ssmParams.dbPort,
//   GA_ID: ssmParams.gaId,
//   HTTP_AUTH_USER: `\${SSM:${sensitiveParams.httpUser}}`,
//   HTTP_AUTH_PASSWORD: `\${SSM:${sensitiveParams.httpPassword}}`,
//   DJANGO_USERNAME: `\${SSM:${sensitiveParams.readerUser}}`,
//   DJANGO_PASSWORD: `\${SSM:${sensitiveParams.readerPassword}}`,
//   DJANGO_ADMIN_USERNAME: `\${SSM:${sensitiveParams.httpUser}}`,
//   DJANGO_ADMIN_PASSWORD: `\${SSM:${sensitiveParams.httpPassword}}`,
//   DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
//   ALLOWED_HOST: '.amazonaws.com',
//   STAGE_ENV: stageConfig.environment,
//   STATIC_URL: `https://${stageConfig.getResourceName('static-assets')}.s3.amazonaws.com/`,
//   WORKING_DIR: '/var/task',
//   BASE_URL: ssmParams.baseUrl,
//   CUSTOM_URL: ssmParams.customUrl,
//   SURVEY_URL: ssmParams.surveyUrl,
//   SIGNUP_URL: ssmParams.signupUrl,
//   DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
//   OIDC_RP_CLIENT_ID: `\${SSM:${sensitiveParams.oidcClientId}}`,
//   OIDC_RP_CLIENT_SECRET: `\${SSM:${sensitiveParams.oidcClientSecret}}`,
//   OIDC_OP_AUTHORIZATION_ENDPOINT: ssmParams.oidcAuthEndpoint,
//   OIDC_OP_TOKEN_ENDPOINT: ssmParams.oidcTokenEndpoint,
//   OIDC_OP_JWKS_ENDPOINT: ssmParams.oidcJwksEndpoint,
//   OIDC_OP_USER_ENDPOINT: ssmParams.oidcUserEndpoint,
//   OIDC_END_EUA_SESSION: ssmParams.oidcEndEuaSession,
//   BASIC_SEARCH_FILTER: ssmParams.basicSearchFilter,
//   QUOTED_SEARCH_FILTER: ssmParams.quotedSearchFilter,
//   SEARCH_HEADLINE_TEXT_MAX: ssmParams.searchHeadlineTextMax,
//   SEARCH_HEADLINE_MIN_WORDS: ssmParams.searchHeadlineMinWords,
//   SEARCH_HEADLINE_MAX_WORDS: ssmParams.searchHeadlineMaxWords,
//   SEARCH_HEADLINE_MAX_FRAGMENTS: ssmParams.searchHeadlineMaxFragments,
//   EUA_FEATUREFLAG: ssmParams.euaFeatureFlag,
//   AWS_STORAGE_BUCKET_NAME: stageConfig.getResourceName(`file-repo-eregs`),
//   TEXT_EXTRACTOR_QUEUE_URL: textExtractorQueue.queueUrl,
//   DEPLOY_NUMBER: process.env.RUN_ID || '',
// };
//     // Common Lambda Configuration
//     const commonLambdaProps = {
//       runtime: lambda.Runtime.PYTHON_3_12,
//       vpc,
//       vpcSubnets: selectedSubnets,
//       securityGroups: [serverlessSG],
//       layers: [pythonLayer],
//       environment: environmentVariables,
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend')),
//     };

//     // Create Log Groups
//     const createLogGroup = (name: string) => new logs.LogGroup(this, `${name}LogGroup`, {
//       logGroupName: stageConfig.aws.lambda(name),
//       retention: logs.RetentionDays.ONE_MONTH,
//     });

//     // Create Lambda Functions
//     const regSiteLambda = new lambda.Function(this, 'RegSiteLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('reg-site'),
//       handler: 'handler.lambda_handler',
//       timeout: cdk.Duration.seconds(30),
//       memorySize: props.lambdaConfig.memorySize,
//       logGroup: createLogGroup('reg-site'),
//     });

//     const migrateLambda = new lambda.Function(this, 'MigrateLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('reg-core-migrate'),
//       handler: 'migrate.handler',
//       timeout: cdk.Duration.seconds(900),
//       memorySize: 1024,
//       logGroup: createLogGroup('reg-core-migrate'),
//     });

//     const createDbLambda = new lambda.Function(this, 'CreateDbLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('createdb'),
//       handler: 'createdb.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       logGroup: createLogGroup('createdb'),
//     });

//     const dropDbLambda = new lambda.Function(this, 'DropDbLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('dropdb'),
//       handler: 'dropdb.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       logGroup: createLogGroup('dropdb'),
//     });

//     const emptyBucketLambda = new lambda.Function(this, 'EmptyBucketLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('empty-bucket'),
//       handler: 'empty_bucket.handler',
//       timeout: cdk.Duration.seconds(900),
//       memorySize: 1024,
//       logGroup: createLogGroup('empty-bucket'),
//     });

//     const createSuLambda = new lambda.Function(this, 'CreateSuLambda', {
//       ...commonLambdaProps,
//       functionName: stageConfig.getResourceName('create-su'),
//       handler: 'createsu.handler',
//       timeout: cdk.Duration.seconds(300),
//       memorySize: 1024,
//       logGroup: createLogGroup('create-su'),
//     });

//     // Create API Gateway
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
//       lambda: regSiteLambda,
//     });

//     // Grant S3 Permissions
//     storageBucket.grantReadWrite(regSiteLambda);
//     storageBucket.grantReadWrite(emptyBucketLambda);

//     // Grant SQS Permissions
//     textExtractorQueue.grantSendMessages(regSiteLambda);

//     // Create WAF
//     const waf = new WafConstruct(this, 'Waf', stageConfig);

//     // Create Stack Outputs
//     const outputs: Record<string, cdk.CfnOutputProps> = {
//       ApiHandlerArn: {
//         value: regSiteLambda.functionArn,
//         description: 'API Handler Lambda function ARN',
//         exportName: stageConfig.getResourceName('api-handler-arn'),
//       },
//       ApiHandlerName: {
//         value: regSiteLambda.functionName,
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
//       StorageBucketName: {
//         value: storageBucket.bucketName,
//         description: 'Storage bucket name',
//         exportName: stageConfig.getResourceName('storage-bucket-name'),
//       },
//     };

//     // Add Lambda Output ARNs
//     const lambdaOutputs = {
//       CreateDbLambdaArn: createDbLambda.functionArn,
//       MigrateLambdaArn: migrateLambda.functionArn,
//       CreateSuLambdaArn: createSuLambda.functionArn,
//       DropDbLambdaArn: dropDbLambda.functionArn,
//       EmptyBucketLambdaArn: emptyBucketLambda.functionArn,
//     };

//     Object.entries(lambdaOutputs).forEach(([name, value]) => {
//       outputs[name] = {
//         value,
//         description: `${name} Lambda function ARN`,
//         exportName: stageConfig.getResourceName(name.toLowerCase()),
//       };
//     });

//     // Create all outputs
//     Object.entries(outputs).forEach(([name, config]) => 
//       new cdk.CfnOutput(this, name, config)
//     );

//     // Add Lambda function permissions for database operations
//     const dbLambdas = [
//       createDbLambda,
//       dropDbLambda,
//       migrateLambda,
//       createSuLambda,
//     ];

//     dbLambdas.forEach(lambdaFn => {
//       lambdaFn.addToRolePolicy(new iam.PolicyStatement({
//         effect: iam.Effect.ALLOW,
//         actions: [
//           'rds:DescribeDBInstances',
//           'rds:DescribeDBClusters',
//         ],
//         resources: ['*'],
//       }));
//     });

//     // Add tags to all Lambda functions
//     const allLambdas = [
//       regSiteLambda,
//       migrateLambda,
//       createDbLambda,
//       dropDbLambda,
//       emptyBucketLambda,
//       createSuLambda,
//     ];

//     const commonTags = {
//       Environment: stageConfig.environment,
//       Service: 'eregs',
//       DeployedBy: 'CDK',
//     };

//     allLambdas.forEach(lambdaFn => {
//       Object.entries(commonTags).forEach(([key, value]) => {
//         cdk.Tags.of(lambdaFn).add(key, value);
//       });
//     });
//   }
// }

