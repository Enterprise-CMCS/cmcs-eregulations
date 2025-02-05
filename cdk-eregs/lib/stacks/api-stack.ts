/**
 * @fileoverview Backend Stack that combines Database and API resources with environment awareness
 */

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
import { DatabaseConstruct } from '../constructs/database-construct';
import { WafConstruct } from '../constructs/waf-construct';
import * as path from 'path';

/**
 * Lambda function configuration interface
 * @interface LambdaConfig
 */
interface LambdaConfig {
  /** Memory size in MB */
  memorySize: number;
  /** Timeout in seconds */
  timeout: number;
  /** Optional concurrent execution limit */
  reservedConcurrentExecutions?: number;
}

/**
 * Environment configuration interface
 * @interface EnvironmentConfig
 */
interface EnvironmentConfig {
  /** VPC ID where resources will be deployed */
  vpcId: string;
  /** Logging level for the application */
  logLevel: string;
  /** List of subnet IDs for resource placement */
  subnetIds: string[];
}

/**
 * Props for the Backend Stack
 * @interface BackendStackProps
 * @extends cdk.StackProps
 */
interface BackendStackProps extends cdk.StackProps {
  /** Lambda function configuration */
  lambdaConfig: LambdaConfig;
  /** Environment-specific configuration */
  environmentConfig: EnvironmentConfig;
}

/**
 * Predefined secret paths in AWS Secrets Manager
 * @const
 */
const SECRETS = {
  OIDC_CREDENTIALS: '/eregulations/oidc/client_credentials',
  DJANGO_CREDENTIALS: '/eregulations/http/django_credentials',
  READER_CREDENTIALS: '/eregulations/http/reader_credentials',
  DB_CREDENTIALS: '/eregulations/db/credentials',
  HTTP_CREDENTIALS: '/eregulations/http/credentials',
} as const;

/**
 * Combined Backend Stack that manages both API and Database resources
 * Handles environment-specific deployments and resource management
 * @class BackendStack
 * @extends cdk.Stack
 */
export class BackendStack extends cdk.Stack {
  /**
   * Creates an instance of BackendStack
   * @param {Construct} scope - The parent construct
   * @param {string} id - The construct ID
   * @param {BackendStackProps} props - Configuration properties
   * @param {StageConfig} stageConfig - Stage-specific configuration
   */
  constructor(scope: Construct, id: string, props: BackendStackProps, stageConfig: StageConfig) {
    super(scope, id, props);

    // ================================
    // SECRETS
    // ================================
    const secrets = {
      oidc: secretsmanager.Secret.fromSecretNameV2(this, 'OidcSecret', SECRETS.OIDC_CREDENTIALS),
      django: secretsmanager.Secret.fromSecretNameV2(this, 'DjangoSecret', SECRETS.DJANGO_CREDENTIALS),
      reader: secretsmanager.Secret.fromSecretNameV2(this, 'ReaderSecret', SECRETS.READER_CREDENTIALS),
      db: secretsmanager.Secret.fromSecretNameV2(this, 'DbSecret', SECRETS.DB_CREDENTIALS),
      http: secretsmanager.Secret.fromSecretNameV2(this, 'HttpSecret', SECRETS.HTTP_CREDENTIALS),
    };

    // ================================
    // VPC & NETWORKING
    // ================================
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId,
    });

    const selectedSubnets: ec2.SubnetSelection = {
      subnets: props.environmentConfig.subnetIds.map(
        (subnetId, index) => ec2.Subnet.fromSubnetId(
          this,
          `PrivateSubnet${index + 1}`,
          subnetId
        )
      ),
    };

    // ================================
    // DATABASE SETUP WITH SAFE IMPORTS
    // ================================
    let databaseSecurityGroup: ec2.ISecurityGroup;
    let databaseEndpoint: string;
    let databaseConstruct: DatabaseConstruct | undefined;

    if (!stageConfig.isEphemeral()) {
      // Create new database for non-ephemeral environments
      databaseConstruct = new DatabaseConstruct(this, 'Database', {
        vpc,
        selectedSubnets,
        stageConfig,
      });
      databaseSecurityGroup = databaseConstruct.dbSecurityGroup;
      databaseEndpoint = databaseConstruct.cluster.clusterEndpoint.hostname;

      // Export database resources if this is dev environment
      if (stageConfig.environment === 'dev') {
        new cdk.CfnOutput(this, 'DevDatabaseEndpoint', {
          value: databaseEndpoint,
          description: 'Dev Database endpoint for ephemeral environments',
          exportName: `${StageConfig.projectName}-dev-db-endpoint`,
        });

        new cdk.CfnOutput(this, 'DevDatabaseSecurityGroup', {
          value: databaseConstruct.dbSecurityGroup.securityGroupId,
          description: 'Dev Database security group ID for ephemeral environments',
          exportName: `${StageConfig.projectName}-dev-db-security-group`,
        });
      }
    } else {
      // For ephemeral environments, try to import from dev
      try {
        // Check if dev exports exist
        const devSgExportName = `${StageConfig.projectName}-dev-db-security-group`;
        const devEndpointExportName = `${StageConfig.projectName}-dev-db-endpoint`;

        // Use Fn.condition to check if the exports exist
        const devDbSgId = cdk.Token.isUnresolved(devSgExportName) ? 
          cdk.Fn.importValue(devSgExportName) : 
          undefined;

        const devDbEndpoint = cdk.Token.isUnresolved(devEndpointExportName) ? 
          cdk.Fn.importValue(devEndpointExportName) : 
          undefined;

        if (!devDbSgId || !devDbEndpoint) {
          throw new Error(
            'Dev database resources not found. Please ensure dev environment is deployed first.'
          );
        }

        databaseSecurityGroup = ec2.SecurityGroup.fromSecurityGroupId(
          this,
          'ImportedDbSG',
          devDbSgId,
          { allowAllOutbound: true }
        );
        databaseEndpoint = devDbEndpoint;
      } catch (error) {
        throw new Error(
          'Cannot deploy ephemeral environment: Dev database does not exist yet. ' +
          'Please deploy dev environment first to create the required database resources.'
        );
      }
    }

    // ================================
    // S3 BUCKET
    // ================================
    const isEphemeral = stageConfig.isEphemeral();
    const storageBucket = new s3.Bucket(this, 'StorageBucket', {
      bucketName: stageConfig.getResourceName(`file-repo-eregs`),
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      autoDeleteObjects: isEphemeral,
      removalPolicy: isEphemeral ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN,
      cors: [
        {
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
          allowedOrigins: ['*'],
          allowedHeaders: ['*'],
          maxAge: 3000,
        },
      ],
    });

    // ================================
    // SECURITY GROUP
    // ================================
    const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: `Security Group for ${stageConfig.stageName} Serverless Functions`,
      allowAllOutbound: true,
      securityGroupName: stageConfig.getResourceName('serverless-security-group'),
    });

    // Add ingress rule to database security group
    databaseSecurityGroup.addIngressRule(
      serverlessSG,
      ec2.Port.tcp(5432),
      'Allow PostgreSQL access from Lambda functions'
    );

    // ================================
    // SQS QUEUE
    // ================================
    const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
      queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
      queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
    });

    // ================================
    // SSM PARAMETERS
    // ================================
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

    // ================================
    // BUILD ID
    // ================================
    const buildId = this.node.tryGetContext('buildId') 
      || process.env.RUN_ID 
      || new Date().getTime().toString();

    // ================================
    // ENVIRONMENT VARIABLES
    // ================================
    const environmentVariables: { [key: string]: string } = {
      DB_NAME: 'eregs',
      DB_USER: 'eregsuser',
      DB_HOST: databaseEndpoint,
      DB_PORT: ssmParams.dbPort,
      GA_ID: ssmParams.gaId,
      DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
      ALLOWED_HOST: '.amazonaws.com',
      STAGE_ENV: stageConfig.stageName,
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
      DB_PASSWORD: secrets.db.secretValueFromJson('DB_PASSWORD').unsafeUnwrap(),
      HTTP_AUTH_USER: secrets.http.secretValueFromJson('HTTP_AUTH_USER').unsafeUnwrap(),
      HTTP_AUTH_PASSWORD: secrets.http.secretValueFromJson('HTTP_AUTH_PASSWORD').unsafeUnwrap(),
      DJANGO_ADMIN_USERNAME: secrets.django.secretValueFromJson('DJANGO_ADMIN_USERNAME').unsafeUnwrap(),
      DJANGO_ADMIN_PASSWORD: secrets.django.secretValueFromJson('DJANGO_ADMIN_PASSWORD').unsafeUnwrap(),
      DJANGO_USERNAME: secrets.reader.secretValueFromJson('DJANGO_USERNAME').unsafeUnwrap(),
      DJANGO_PASSWORD: secrets.reader.secretValueFromJson('DJANGO_PASSWORD').unsafeUnwrap(),
      OIDC_RP_CLIENT_ID: secrets.oidc.secretValueFromJson('OIDC_RP_CLIENT_ID').unsafeUnwrap(),
      OIDC_RP_CLIENT_SECRET: secrets.oidc.secretValueFromJson('OIDC_RP_CLIENT_SECRET').unsafeUnwrap(),
    };

    // ================================
    // LOG GROUPS
    // ================================
    /**
     * Creates a CloudWatch Log Group for Lambda functions
     * @param {string} name - Base name for the log group
     * @returns {logs.LogGroup} Created log group
     */
    const createLogGroup = (name: string): logs.LogGroup => 
      new logs.LogGroup(this, `${name}LogGroup`, {
        logGroupName: stageConfig.aws.lambda(name),
        retention: logs.RetentionDays.ONE_MONTH,
      });

    // ================================
    // LAMBDA FACTORY
    // ================================
    /**
     * Creates a Docker-based Lambda function with standard configuration
     * @param {string} name - Function name
     * @param {string} dockerFile - Name of the Dockerfile
     * @param {string} handler - Handler function path
     * @param {number} [timeout=300] - Function timeout in seconds
     * @returns {lambda.DockerImageFunction} Created Lambda function
     */
    const createDockerLambda = (
      name: string,
      dockerFile: string,
      handler: string,
      timeout: number = 300,
    ): lambda.DockerImageFunction => {
      const lambdaFunction = new lambda.DockerImageFunction(this, `${name}Lambda`, {
        functionName: stageConfig.getResourceName(name.toLowerCase()),
        code: lambda.DockerImageCode.fromImageAsset(
          path.join(__dirname, '../../../solution/backend/'),
          {
            file: dockerFile,
            cmd: [handler],
            buildArgs: {
              BUILD_ID: buildId,
            },
          },
        ),
        vpc,
        vpcSubnets: selectedSubnets,
        securityGroups: [serverlessSG],
        timeout: cdk.Duration.seconds(timeout),
        memorySize: props.lambdaConfig.memorySize || 4096,
        environment: environmentVariables,
        logGroup: createLogGroup(name.toLowerCase()),
      });

      // Grant read access to secrets
      Object.values(secrets).forEach(secret => secret.grantRead(lambdaFunction));

      // Add tags from StageConfig
      Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
        cdk.Tags.of(lambdaFunction).add(key, value);
      });

      return lambdaFunction;
    };

    // ================================
    // LAMBDA FUNCTIONS
    // ================================
    const regSiteLambda = createDockerLambda('RegSite', 'regsite.Dockerfile', 'handler.handler', 30);
    const migrateLambda = createDockerLambda('Migrate', 'migrate.Dockerfile', 'migrate.handler', 900);
    const createDbLambda = createDockerLambda('CreateDb', 'createdb.Dockerfile', 'createdb.handler');
    const dropDbLambda = createDockerLambda('DropDb', 'dropdb.Dockerfile', 'dropdb.handler');
    const createSuLambda = createDockerLambda('CreateSu', 'createsu.Dockerfile', 'createsu.handler');

    let authorizerLambda;
    if (stageConfig.environment !== 'prod') {
      authorizerLambda = createDockerLambda(
        'Authorizer',
        'authorizer.Dockerfile',
        'authorizer.handler',
        30
      );
    }

    // ================================
    // API GATEWAY
    // ================================
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
      authorizerLambda,
    });

    // ================================
    // PERMISSIONS
    // ================================
    storageBucket.grantReadWrite(regSiteLambda);
    textExtractorQueue.grantSendMessages(regSiteLambda);

    // DB inspection permissions
    [createDbLambda, dropDbLambda, migrateLambda, createSuLambda].forEach(lambdaFn => {
      lambdaFn.addToRolePolicy(
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: ['rds:DescribeDBInstances', 'rds:DescribeDBClusters'],
          resources: ['*'],
        }),
      );
    });

    // ================================
    // WAF
    // ================================
    const waf = new WafConstruct(this, 'Waf', stageConfig);
    waf.associateWithApiGateway(api.api);

    // ================================
    // STACK OUTPUTS
    // ================================
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

    // Additional Lambda outputs
    const lambdaOutputs = {
      CreateDbLambdaArn: createDbLambda.functionArn,
      MigrateLambdaArn: migrateLambda.functionArn,
      CreateSuLambdaArn: createSuLambda.functionArn,
      DropDbLambdaArn: dropDbLambda.functionArn,
    };

    Object.entries(lambdaOutputs).forEach(([name, value]) => {
      outputs[name] = {
        value,
        description: `${name} Lambda function ARN`,
        exportName: stageConfig.getResourceName(name.toLowerCase()),
      };
    });

    if (authorizerLambda) {
      outputs.AuthorizerLambdaArn = {
        value: authorizerLambda.functionArn,
        description: 'Authorizer Lambda function ARN',
        exportName: stageConfig.getResourceName('authorizer-lambda-arn'),
      };
    }

    // Create all outputs
    Object.entries(outputs).forEach(([name, config]) => {
      new cdk.CfnOutput(this, name, config);
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
//   aws_secretsmanager as secretsmanager,
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
//   private createOrImportSecurityGroup(vpc: ec2.IVpc, stageConfig: StageConfig): ec2.ISecurityGroup {
//     // For ephemeral environments, try to import dev security group
//     if (stageConfig.isEphemeral()) {
//       const devSgExportName = `${StageConfig.projectName}-dev-serverless-security-group`;
      
//       // Check if the export exists before trying to import
//       try {
//         // Use Fn.condition to check if the export exists
//         const devSgId = cdk.Token.isUnresolved(devSgExportName) ? 
//           cdk.Fn.importValue(devSgExportName) : 
//           undefined;
  
//         if (devSgId) {
//           return ec2.SecurityGroup.fromSecurityGroupId(
//             this, 
//             'ImportedDevServerlessSG',
//             devSgId,
//             { allowAllOutbound: true }
//           );
//         }
//       } catch (error) {
//         // Log warning but continue with creating new security group
//         console.warn('Dev security group not found for ephemeral environment, creating new one');
//       }
//     }

//     // Create new security group with standardized naming
//     const sgName = stageConfig.getResourceName('serverless-security-group');
//     const serverlessSG = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: `Security Group for ${stageConfig.stageName} Serverless Functions`,
//       allowAllOutbound: true,
//       securityGroupName: sgName,
//     });

//     // Add inbound rules
//     serverlessSG.addIngressRule(
//       ec2.Peer.anyIpv4(),
//       ec2.Port.tcp(443),
//       'Allow HTTPS inbound'
//     );

//     // Export the security group ID
//     new cdk.CfnOutput(this, 'ServerlessSecurityGroupOutput', {
//       value: serverlessSG.securityGroupId,
//       exportName: sgName,
//       description: `Security Group ID for ${stageConfig.stageName} environment`
//     });

//     // Add tags using StageConfig
//     const tags = stageConfig.getStackTags();
//     Object.entries(tags).forEach(([key, value]) => {
//       cdk.Tags.of(serverlessSG).add(key, value);
//     });

//     return serverlessSG;
//   }

//   constructor(scope: Construct, id: string, props: APIStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     // ================================
//     // SECRETS
//     // ================================
//     const SECRETS = {
//       OIDC_CREDENTIALS: '/eregulations/oidc/client_credentials',
//       DJANGO_CREDENTIALS: '/eregulations/http/django_credentials',
//       READER_CREDENTIALS: '/eregulations/http/reader_credentials',
//       DB_CREDENTIALS: '/eregulations/db/credentials',
//       HTTP_CREDENTIALS: '/eregulations/http/credentials',
//     };

//     const oidcSecret = secretsmanager.Secret.fromSecretNameV2(this, 'OidcSecret', SECRETS.OIDC_CREDENTIALS);
//     const djangoSecret = secretsmanager.Secret.fromSecretNameV2(this, 'DjangoSecret', SECRETS.DJANGO_CREDENTIALS);
//     const readerSecret = secretsmanager.Secret.fromSecretNameV2(this, 'ReaderSecret', SECRETS.READER_CREDENTIALS);
//     const dbSecret = secretsmanager.Secret.fromSecretNameV2(this, 'DbSecret', SECRETS.DB_CREDENTIALS);
//     const httpSecret = secretsmanager.Secret.fromSecretNameV2(this, 'HttpSecret', SECRETS.HTTP_CREDENTIALS);

//     // ================================
//     // NON-SENSITIVE PARAMETERS
//     // ================================
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

//     // ================================
//     // BUILD ID FOR UNIQUE DOCKER TAGS
//     // ================================
//     const buildId = this.node.tryGetContext('buildId') 
//       || process.env.RUN_ID 
//       || new Date().getTime().toString();

//     // ================================
//     // CREATE S3 BUCKET
//     // ================================
//     const isEphemeral = stageConfig.isEphemeral();
//     const storageBucket = new s3.Bucket(this, 'StorageBucket', {
//       bucketName: stageConfig.getResourceName(`file-repo-eregs`),
//       encryption: s3.BucketEncryption.S3_MANAGED,
//       blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
//       enforceSSL: true,
//       autoDeleteObjects: isEphemeral,
//       removalPolicy: isEphemeral ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN,
//       cors: [
//         {
//           allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
//           allowedOrigins: ['*'],
//           allowedHeaders: ['*'],
//           maxAge: 3000,
//         },
//       ],
//     });

//     // ================================
//     // VPC & SECURITY GROUP
//     // ================================
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: [
//         ec2.Subnet.fromSubnetId(this, 'PrivateSubnet', props.environmentConfig.subnetIds[0]),
//       ],
//     };

//     // Get the appropriate security group based on environment
//     const serverlessSG = this.createOrImportSecurityGroup(vpc, stageConfig);

//     // ================================
//     // EXISTING SQS QUEUE
//     // ================================
//     const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
//       queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
//       queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
//     });

//     // ================================
//     // ENVIRONMENT VARIABLES
//     // ================================
//     const environmentVariables: { [key: string]: string } = {
//       DB_NAME: 'eregs',
//       DB_USER: 'eregsuser',
//       DB_HOST: ssmParams.dbHost,
//       DB_PORT: ssmParams.dbPort,
//       GA_ID: ssmParams.gaId,
//       DJANGO_SETTINGS_MODULE: ssmParams.djangoSettingsModule,
//       ALLOWED_HOST: '.amazonaws.com',
//       STAGE_ENV: stageConfig.stageName,
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
//       DB_PASSWORD: dbSecret.secretValueFromJson('DB_PASSWORD').unsafeUnwrap(),
//       HTTP_AUTH_USER: httpSecret.secretValueFromJson('HTTP_AUTH_USER').unsafeUnwrap(),
//       HTTP_AUTH_PASSWORD: httpSecret.secretValueFromJson('HTTP_AUTH_PASSWORD').unsafeUnwrap(),
//       DJANGO_ADMIN_USERNAME: djangoSecret.secretValueFromJson('DJANGO_ADMIN_USERNAME').unsafeUnwrap(),
//       DJANGO_ADMIN_PASSWORD: djangoSecret.secretValueFromJson('DJANGO_ADMIN_PASSWORD').unsafeUnwrap(),
//       DJANGO_USERNAME: readerSecret.secretValueFromJson('DJANGO_USERNAME').unsafeUnwrap(),
//       DJANGO_PASSWORD: readerSecret.secretValueFromJson('DJANGO_PASSWORD').unsafeUnwrap(),
//       OIDC_RP_CLIENT_ID: oidcSecret.secretValueFromJson('OIDC_RP_CLIENT_ID').unsafeUnwrap(),
//       OIDC_RP_CLIENT_SECRET: oidcSecret.secretValueFromJson('OIDC_RP_CLIENT_SECRET').unsafeUnwrap(),
//     };

//     // ================================
//     // CREATE LOG GROUPS
//     // ================================
//     const createLogGroup = (name: string) =>
//       new logs.LogGroup(this, `${name}LogGroup`, {
//         logGroupName: stageConfig.aws.lambda(name),
//         retention: logs.RetentionDays.ONE_MONTH,
//       });

//     // ================================
//     // HELPER: CREATE DOCKER-BASED LAMBDAS
//     // ================================
//     const createDockerLambda = (
//       name: string,
//       dockerFile: string,
//       handler: string,
//       timeout: number = 300,
//     ) => {
//       const lambdaFunction = new lambda.DockerImageFunction(this, `${name}Lambda`, {
//         functionName: stageConfig.getResourceName(name.toLowerCase()),
//         code: lambda.DockerImageCode.fromImageAsset(
//           path.join(__dirname, '../../../solution/backend/'),
//           {
//             file: dockerFile,
//             cmd: [handler],
//             buildArgs: {
//               BUILD_ID: buildId,
//             },
//           },
//         ),
//         vpc,
//         vpcSubnets: selectedSubnets,
//         securityGroups: [serverlessSG],
//         timeout: cdk.Duration.seconds(timeout),
//         memorySize: props.lambdaConfig.memorySize || 4096,
//         environment: environmentVariables,
//         logGroup: createLogGroup(name.toLowerCase()),
//       });

//       // Grant read access to secrets
//       oidcSecret.grantRead(lambdaFunction);
//       djangoSecret.grantRead(lambdaFunction);
//       readerSecret.grantRead(lambdaFunction);
//       dbSecret.grantRead(lambdaFunction);
//       httpSecret.grantRead(lambdaFunction);

//       // Add tags from StageConfig
//       Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
//         cdk.Tags.of(lambdaFunction).add(key, value);
//       });

//       return lambdaFunction;
//     };

//     // ================================
//     // DEFINE LAMBDAS
//     // ================================
//     const regSiteLambda = createDockerLambda('RegSite', 'regsite.Dockerfile', 'handler.handler', 30);
//     const migrateLambda = createDockerLambda('Migrate', 'migrate.Dockerfile', 'migrate.handler', 900);
//     const createDbLambda = createDockerLambda('CreateDb', 'createdb.Dockerfile', 'createdb.handler');
//     const dropDbLambda = createDockerLambda('DropDb', 'dropdb.Dockerfile', 'dropdb.handler');
//     const createSuLambda = createDockerLambda('CreateSu', 'createsu.Dockerfile', 'createsu.handler');

//     // Create authorizer Lambda for non-prod environments
//     let authorizerLambda;
//     if (stageConfig.environment !== 'prod') {
//       authorizerLambda = createDockerLambda(
//         'Authorizer',
//         'authorizer.Dockerfile',
//         'authorizer.handler',
//         30
//       );
//     }

//     // ================================
//     // CREATE API GATEWAY CONSTRUCT
//     // ================================
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
//       authorizerLambda: authorizerLambda,
//     });

//     // ================================
//     // PERMISSIONS
//     // ================================
//     // S3
//     storageBucket.grantReadWrite(regSiteLambda);

//     // SQS
//     textExtractorQueue.grantSendMessages(regSiteLambda);

//     // ================================
//     // WAF
//     // ================================
//     const waf = new WafConstruct(this, 'Waf', stageConfig);

//     // ALLOW DB INSPECTION (RDS: Describe Only)
//     const dbLambdas = [createDbLambda, dropDbLambda, migrateLambda, createSuLambda];
//     dbLambdas.forEach(lambdaFn => {
//       lambdaFn.addToRolePolicy(
//         new iam.PolicyStatement({
//           effect: iam.Effect.ALLOW,
//           actions: ['rds:DescribeDBInstances', 'rds:DescribeDBClusters'],
//           resources: ['*'],
//         }),
//       );
//     });

//     // ================================
//     // TAG ALL LAMBDAS
//     // ================================
//     const allLambdas = [
//       regSiteLambda,
//       migrateLambda,
//       createDbLambda,
//       dropDbLambda,
//       createSuLambda,
//     ];

//     if (authorizerLambda) {
//       allLambdas.push(authorizerLambda);
//     }

//     // Apply stage-specific tags to all lambdas
//     allLambdas.forEach(lambdaFn => {
//       Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
//         cdk.Tags.of(lambdaFn).add(key, value);
//       });
//     });

//     // ================================
//     // STACK OUTPUTS
//     // ================================
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
//       // WAF outputs
//       WafAclArn: {
//         value: waf.webAcl.attrArn,
//         description: 'WAF Web ACL ARN',
//         exportName: stageConfig.getResourceName('waf-acl-arn'),
//       },
//       WafAclId: {
//         value: waf.webAcl.attrId,
//         description: 'WAF Web ACL ID',
//         exportName: stageConfig.getResourceName('waf-acl-id'),
//       },
//       WafLogGroup: {
//         value: waf.getLogGroupArn(),
//         description: 'WAF Log Group ARN',
//         exportName: stageConfig.getResourceName('waf-log-group-arn'),
//       },
//     };

//     // Additional Lambda outputs
//     const lambdaOutputs = {
//       CreateDbLambdaArn: createDbLambda.functionArn,
//       MigrateLambdaArn: migrateLambda.functionArn,
//       CreateSuLambdaArn: createSuLambda.functionArn,
//       DropDbLambdaArn: dropDbLambda.functionArn,
//     };

//     Object.entries(lambdaOutputs).forEach(([name, value]) => {
//       outputs[name] = {
//         value,
//         description: `${name} Lambda function ARN`,
//         exportName: stageConfig.getResourceName(name.toLowerCase()),
//       };
//     });

//     // Create all outputs
//     Object.entries(outputs).forEach(([name, config]) => {
//       new cdk.CfnOutput(this, name, config);
//     });

//     // ================================
//     // ASSOCIATE WAF WITH API GATEWAY
//     // ================================
//     waf.associateWithApiGateway(api.api);
//   }
// }
