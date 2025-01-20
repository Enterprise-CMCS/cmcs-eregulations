import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_s3 as s3,
  aws_lambda as lambda,
  aws_sqs as sqs,
  aws_ssm as ssm,
  aws_logs as logs,
  aws_iam as iam,
  aws_secretsmanager as secretsmanager,
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

    // Define secret paths
    const SECRETS = {
      OIDC_CREDENTIALS: '/eregulations/oidc/client_credentials',
      DJANGO_CREDENTIALS: '/eregulations/http/django_credentials',
      READER_CREDENTIALS: '/eregulations/http/reader_credentials',
      DB_CREDENTIALS: '/eregulations/db/credentials',
      HTTP_CREDENTIALS: '/eregulations/http/credentials'
    };

    const oidcSecret = secretsmanager.Secret.fromSecretNameV2(this, 'OidcSecret', SECRETS.OIDC_CREDENTIALS);
    const djangoSecret = secretsmanager.Secret.fromSecretNameV2(this, 'DjangoSecret', SECRETS.DJANGO_CREDENTIALS);
    const readerSecret = secretsmanager.Secret.fromSecretNameV2(this, 'ReaderSecret', SECRETS.READER_CREDENTIALS);
    const dbSecret = secretsmanager.Secret.fromSecretNameV2(this, 'DbSecret', SECRETS.DB_CREDENTIALS);
    const httpSecret = secretsmanager.Secret.fromSecretNameV2(this, 'HttpSecret', SECRETS.HTTP_CREDENTIALS);

    // For non-sensitive parameters
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

    // Environment variables - combining secrets and non-sensitive values
    const environmentVariables: { [key: string]: string } = {
      // Non-sensitive values
      DB_NAME: 'eregs',
      DB_USER: 'eregsuser',
      DB_HOST: ssmParams.dbHost,
      DB_PORT: ssmParams.dbPort,
      GA_ID: ssmParams.gaId,
      DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
      ALLOWED_HOST: '.amazonaws.com',
      STAGE_ENV: stageConfig.environment,
      STATIC_URL: cdk.Fn.importValue(stageConfig.getResourceName('static-url')) + '/',
      WORKING_DIR: '/var/task',
      BASE_URL: ssmParams.baseUrl,
      CUSTOM_URL: ssmParams.customUrl,
      SURVEY_URL: ssmParams.surveyUrl,
      SIGNUP_URL: ssmParams.signupUrl,
      DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
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
      // Secret values with correct keys
      DB_PASSWORD: dbSecret.secretValueFromJson('DB_PASSWORD').unsafeUnwrap(),
      HTTP_AUTH_USER: httpSecret.secretValueFromJson('HTTP_AUTH_USER').unsafeUnwrap(),
      HTTP_AUTH_PASSWORD: httpSecret.secretValueFromJson('HTTP_AUTH_PASSWORD').unsafeUnwrap(),
      
      // Django admin credentials
      DJANGO_ADMIN_USERNAME: djangoSecret.secretValueFromJson('DJANGO_ADMIN_USERNAME').unsafeUnwrap(),
      DJANGO_ADMIN_PASSWORD: djangoSecret.secretValueFromJson('DJANGO_ADMIN_PASSWORD').unsafeUnwrap(),
      
      // Django reader credentials (used as regular Django credentials)
      DJANGO_USERNAME: readerSecret.secretValueFromJson('DJANGO_USERNAME').unsafeUnwrap(),
      DJANGO_PASSWORD: readerSecret.secretValueFromJson('DJANGO_PASSWORD').unsafeUnwrap(),
      
      // OIDC credentials
      OIDC_RP_CLIENT_ID: oidcSecret.secretValueFromJson('OIDC_RP_CLIENT_ID').unsafeUnwrap(),
      OIDC_RP_CLIENT_SECRET: oidcSecret.secretValueFromJson('OIDC_RP_CLIENT_SECRET').unsafeUnwrap(),

    };

    // Create Log Groups
    const createLogGroup = (name: string) => new logs.LogGroup(this, `${name}LogGroup`, {
      logGroupName: stageConfig.aws.lambda(name),
      retention: logs.RetentionDays.ONE_MONTH,
    });

    // Create Docker Lambda Functions with common configuration
    const createDockerLambda = (name: string, dockerFile: string, handler: string, timeout: number = 300) => {
      const lambdaFunction = new lambda.DockerImageFunction(this, `${name}Lambda`, {
        functionName: stageConfig.getResourceName(name.toLowerCase()),
        code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/backend/'), {
          file: dockerFile,
          cmd: [handler]
        }),
        vpc,
        vpcSubnets: selectedSubnets,
        securityGroups: [serverlessSG],
        timeout: cdk.Duration.seconds(timeout),
        memorySize: 4096,
        environment: environmentVariables,
        logGroup: createLogGroup(name.toLowerCase())
      });

      // Grant Secrets Manager access to Lambda for all secrets
      oidcSecret.grantRead(lambdaFunction);
      djangoSecret.grantRead(lambdaFunction);
      readerSecret.grantRead(lambdaFunction);
      dbSecret.grantRead(lambdaFunction);
      httpSecret.grantRead(lambdaFunction);

      return lambdaFunction;
    };

    // Create Lambda functions
    const regSiteLambda = createDockerLambda('RegSite', 'regsite.Dockerfile', 'handler.lambda_handler', 30);
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
      // WAF outputs
      WafAclArn: {
        value: waf.webAcl.attrArn,
        description: 'WAF Web ACL ARN',
        exportName: stageConfig.getResourceName('waf-acl-arn'),
      },
      WafAclId: {
        value: waf.webAcl.attrId,
        description: 'WAF Web ACL ID',
        exportName: stageConfig.getResourceName('waf-acl-id'),
      },
      WafLogGroup: {
        value: waf.getLogGroupArn(),
        description: 'WAF Log Group ARN',
        exportName: stageConfig.getResourceName('waf-log-group-arn'),
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

    // Associate WAF with API Gateway
    waf.associateWithApiGateway(api.api);
  }
}
    // const outputs: Record<string, cdk.CfnOutputProps> = {
    //   ApiHandlerArn: {
    //     value: regSiteLambda.functionArn,
    //     description: 'API Handler Lambda function ARN',
    //     exportName: stageConfig.getResourceName('api-handler-arn'),
    //   },
    //   ApiHandlerName: {
    //     value: regSiteLambda.functionName,
    //     description: 'API Handler Lambda function name',
    //     exportName: stageConfig.getResourceName('api-handler-name'),
    //   },
    //   StorageBucketName: {
    //     value: storageBucket.bucketName,
    //     description: 'Name of the S3 bucket for file repository',
    //     exportName: stageConfig.getResourceName('storage-bucket-name'),
    //   },
    //   TextExtractorQueueUrl: {
    //     value: textExtractorQueue.queueUrl,
    //     description: 'URL of the SQS queue for text extraction',
    //     exportName: stageConfig.getResourceName('text-extractor-queue-url'),
    //   },
    //   WafWebAclArn: {
    //     value: waf.webAclArn,
    //     description: 'ARN of the WAF Web ACL',
    //     exportName: stageConfig.getResourceName('waf-web-acl-arn'),
    //   },
    // };

    // Object.entries(outputs).forEach(([key, props]) => {
    //   new cdk.CfnOutput(this, key, props);
    // });


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

//     // Required SSM parameters that will be accessed at runtime
//     const REQUIRED_SSM_PARAMS = {
//       DB_PASSWORD: '/eregulations/db/password',
//       HTTP_AUTH_USER: '/eregulations/http/user',
//       HTTP_AUTH_PASSWORD: '/eregulations/http/password',
//       DJANGO_USERNAME: '/eregulations/http/reader_user',
//       DJANGO_PASSWORD: '/eregulations/http/reader_password',
//       DJANGO_ADMIN_USERNAME: '/eregulations/http/user',
//       DJANGO_ADMIN_PASSWORD: '/eregulations/http/password',
//       OIDC_RP_CLIENT_ID: '/eregulations/oidc/client_id',
//       OIDC_RP_CLIENT_SECRET: '/eregulations/oidc/client_secret',
//     };

//     // For non-sensitive parameters
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

//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//     // Environment variables - non-sensitive values only
//     const environmentVariables = {
//       DB_NAME: 'eregs',
//       DB_USER: 'eregsuser',
//       DB_HOST: ssmParams.dbHost,
//       DB_PORT: ssmParams.dbPort,
//       GA_ID: ssmParams.gaId,
//       DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
//       ALLOWED_HOST: '.amazonaws.com',
//       STAGE_ENV: stageConfig.environment,
//       STATIC_URL: cdk.Fn.importValue(stageConfig.getResourceName('static-url')) + '/',
//       WORKING_DIR: '/var/task',
//       BASE_URL: ssmParams.baseUrl,
//       CUSTOM_URL: ssmParams.customUrl,
//       SURVEY_URL: ssmParams.surveyUrl,
//       SIGNUP_URL: ssmParams.signupUrl,
//       DEMO_VIDEO_URL: ssmParams.demoVideoUrl,
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

//     // Create SSM access policy for both regular and secure parameters
//     const ssmAccessPolicy = new iam.PolicyStatement({
//       effect: iam.Effect.ALLOW,
//       actions: [
//         'ssm:GetParameter',
//         'ssm:GetParameters',
//         'ssm:GetParametersByPath'
//       ],
//       resources: [
//         ...Object.values(REQUIRED_SSM_PARAMS).map(param => 
//           `arn:aws:ssm:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:parameter${param}`
//         ),
//         `arn:aws:ssm:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:parameter/eregulations/*`,
//         `arn:aws:ssm:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:parameter/account_vars/*`
//       ],
//     });

//     // Create Docker Lambda Functions with common configuration
//     const createDockerLambda = (name: string, dockerFile: string, handler: string, timeout: number = 300) => {
//       const lambdaFunction = new lambda.DockerImageFunction(this, `${name}Lambda`, {
//         functionName: stageConfig.getResourceName(name.toLowerCase()),
//         code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/backend'), {
//           file: dockerFile,
//           cmd: [handler]
//         }),
//         vpc,
//         vpcSubnets: selectedSubnets,
//         securityGroups: [serverlessSG],
//         timeout: cdk.Duration.seconds(timeout),
//         memorySize: 4096,
//         environment: environmentVariables,
//         logGroup: createLogGroup(name.toLowerCase())
//       });

//       // Add SSM access policy to each Lambda
//       lambdaFunction.addToRolePolicy(ssmAccessPolicy);

//       return lambdaFunction;
//     };

//     // Create Lambda functions
//     const regSiteLambda = createDockerLambda('RegSite', 'regsite.Dockerfile', 'handler.lambda_handler', 30);
//     const migrateLambda = createDockerLambda('Migrate', 'migrate.Dockerfile', 'migrate.handler', 900);
//     const createDbLambda = createDockerLambda('CreateDb', 'createdb.Dockerfile', 'createdb.handler');
//     const dropDbLambda = createDockerLambda('DropDb', 'dropdb.Dockerfile', 'dropdb.handler');
//     const emptyBucketLambda = createDockerLambda('EmptyBucket', 'empty_bucket.Dockerfile', 'empty_bucket.handler', 900);
//     const createSuLambda = createDockerLambda('CreateSu', 'createsu.Dockerfile', 'createsu.handler');

//     // Create API Gateway
//     const api = new ApiConstruct(this, 'Api', {
//       vpc,
//       securityGroup: serverlessSG,
//       environmentVariables,
//       storageBucketName: storageBucket.bucketName,
//       queueUrl: textExtractorQueue.queueUrl,
//       lambdaConfig: props.lambdaConfig,
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

