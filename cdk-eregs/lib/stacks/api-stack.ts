/**
 * @fileoverview Backend Stack that combines Database and API resources with environment awareness
 * Uses SSM for database configuration and handles ephemeral environments
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
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import { ApiConstruct } from '../constructs/api-construct';
import { DatabaseConstruct } from '../constructs/database-construct';
import { WafConstruct } from '../constructs/waf-construct';
import * as path from 'path';

/**
 * Configuration for Lambda functions
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
 * Environment configuration
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
 * Security Group Handler class for creating or importing security groups
 */
class SecurityGroupHandler {
    /**
     * Creates or imports a security group based on environment type
     */
    static createOrImportSecurityGroup(
        scope: Construct,
        vpc: ec2.IVpc,
        stageConfig: StageConfig
    ): ec2.ISecurityGroup {
        if (stageConfig.isEphemeral()) {
            try {
                // For ephemeral, import dev's serverless SG from SSM
                const serverlessSgId = ssm.StringParameter.valueForStringParameter(
                    scope,
                    '/eregulations/aws/cdk_securitygroupid'
                );

                return ec2.SecurityGroup.fromSecurityGroupId(
                    scope,
                    'ImportedServerlessSG',
                    serverlessSgId,
                    { allowAllOutbound: true }
                );
            } catch (err) {
                throw new Error(
                    'Failed to get dev serverless security group from SSM. ' +
                    'Ensure dev environment exists and SSM parameter is set. ' +
                    `Error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`
                );
            }
        }

        // For non-ephemeral environments, create new security group
        const serverlessSG = new ec2.SecurityGroup(scope, 'ServerlessSecurityGroup', {
            vpc,
            description: `Security Group for ${stageConfig.stageName} Serverless Functions`,
            allowAllOutbound: true,
            securityGroupName: stageConfig.getResourceName('serverless-security-group'),
        });

        // Add inbound rules
        serverlessSG.addIngressRule(
            ec2.Peer.anyIpv4(),
            ec2.Port.tcp(443),
            'Allow HTTPS inbound'
        );

        return serverlessSG;
    }
}

/**
 * Paths for AWS Secrets Manager secrets
 * @const
 */
const SECRET_NAMES = {
    OIDC_CREDENTIALS: '/eregulations/oidc/client_credentials',
    DJANGO_CREDENTIALS: '/eregulations/http/django_credentials',
    READER_CREDENTIALS: '/eregulations/http/reader_credentials',
    DB_CREDENTIALS: '/eregulations/db/credentials',
    HTTP_CREDENTIALS: '/eregulations/http/credentials',
} as const;

/**
 * Combined Backend Stack for managing API and Database resources
 * @class BackendStack
 * @extends cdk.Stack
 */
export class BackendStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: BackendStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

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

        // Create or import security group using the handler
        const serverlessSG = SecurityGroupHandler.createOrImportSecurityGroup(this, vpc, stageConfig);

        // ================================
        // DATABASE SETUP
        // ================================
        let databaseEndpoint: string;
        let databasePort: string;
        let databaseConstruct: DatabaseConstruct | undefined;

        if (!stageConfig.isEphemeral()) {
            // For non-ephemeral environments
            databaseConstruct = new DatabaseConstruct(this, 'Database', {
                vpc,
                selectedSubnets,
                stageConfig,
                serverlessSecurityGroup: serverlessSG,
            });

            databaseEndpoint = databaseConstruct.cluster.clusterEndpoint.hostname;
            databasePort = databaseConstruct.cluster.clusterEndpoint.port.toString();
        } else {
            // For ephemeral environments, use dev's database settings
            try {
                databaseEndpoint = ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/cdk_host');
                databasePort = ssm.StringParameter.valueForStringParameter(this, '/eregulations/db/port');
            } catch (err) {
                throw new Error(
                    'Failed to get dev database configuration from SSM. ' +
                    'Ensure SSM parameters and secrets exist. ' +
                    `Error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`
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
        // SQS QUEUES
        // ================================
        const textExtractorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedTextExtractorQueue', {
            queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-url')),
            queueArn: cdk.Fn.importValue(stageConfig.getResourceName('text-extractor-queue-arn')),
        });

        const embeddingGeneratorQueue = sqs.Queue.fromQueueAttributes(this, 'ImportedEmbeddingGeneratorQueue', {
            queueUrl: cdk.Fn.importValue(stageConfig.getResourceName('embedding-generator-queue-url')),
            queueArn: cdk.Fn.importValue(stageConfig.getResourceName('embedding-generator-queue-arn')),
        });

        // ================================
        // SSM PARAMETERS
        // ================================
        const ssmParams = {
            dbHost: databaseEndpoint,
            dbPort: databasePort,
            gaId: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/google_analytics'),
            djangoSettingsModule: ssm.StringParameter.valueForStringParameter(this, '/eregulations/django_settings_module'),
            baseUrl: ssm.StringParameter.valueForStringParameter(this, '/eregulations/base_url'),
            customUrl: stageConfig.stageName === "prod" ? ssm.StringParameter.valueForStringParameter(this, '/eregulations/custom_url') : "",
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
        const buildId = this.node.tryGetContext('buildId') || process.env.RUN_ID || new Date().getTime().toString();

        // ================================
        // ENVIRONMENT VARIABLES
        // ================================
        const environmentVariables: { [key: string]: string } = {
            DB_SECRET: SECRET_NAMES.DB_CREDENTIALS,
            DB_NAME: stageConfig.databaseName,
            DB_HOST: databaseEndpoint,
            DB_PORT: databasePort,
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
            OIDC_RP_CLIENT_SECRET: SECRET_NAMES.OIDC_CREDENTIALS,
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
            EMBEDDING_GENERATOR_QUEUE_URL: embeddingGeneratorQueue.queueUrl,
            DEPLOY_NUMBER: buildId,
            HTTP_AUTH_SECRET: SECRET_NAMES.HTTP_CREDENTIALS,
            DJANGO_SECRET: SECRET_NAMES.DJANGO_CREDENTIALS,
            READER_SECRET: SECRET_NAMES.READER_CREDENTIALS,
        };

        // ================================
        // LOG GROUPS
        // ================================
        const createLogGroup = (name: string): logs.LogGroup =>
            new logs.LogGroup(this, `${name}LogGroup`, {
                logGroupName: stageConfig.aws.lambda(name),
                retention: logs.RetentionDays.ONE_MONTH,
            });

        // ================================
        // LAMBDA FACTORY
        // ================================
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
        const createDbLambda = createDockerLambda('CreateDb', 'createdb.Dockerfile', 'createdb.handler', 900);
        const dropDbLambda = createDockerLambda('DropDb', 'dropdb.Dockerfile', 'dropdb.handler');
        const createSuLambda = createDockerLambda('CreateSu', 'createsu.Dockerfile', 'createsu.handler');

        // Create authorizer Lambda for non-prod environments
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

        // AWS Secret Manager permissions
        [regSiteLambda, migrateLambda, createDbLambda, dropDbLambda, createSuLambda, authorizerLambda].forEach(lambdaFn => {
            lambdaFn?.addToRolePolicy(
                new iam.PolicyStatement({
                    effect: iam.Effect.ALLOW,
                    actions: ['secretsmanager:GetSecretValue'],
                    resources: Object.values(SECRET_NAMES).map(secretName => `arn:aws:secretsmanager:${this.region}:${this.account}:secret:${secretName}*`),
                }),
            );
        });

        // TEMPORARY: Allow function to use Bedrock (Titan Embeddings model V2)
        regSiteLambda.addToRolePolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                actions: [
                    'bedrock:InvokeModel',
                    'bedrock:BatchInvokeModel',
                    'bedrock:ListModels',
                ],
                resources: [
                    'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0',
                ],
            }),
        );

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
            ApiEndpoint: {
                value: api.api.url,
                description: 'API Gateway endpoint URL',
                exportName: stageConfig.getResourceName('api-endpoint'),
            },
            StorageBucketName: {
                value: storageBucket.bucketName,
                description: 'Storage bucket name',
                exportName: stageConfig.getResourceName('storage-bucket-name'),
            },
        };

        // Lambda ARN outputs
        const lambdaOutputs = {
            MigrateLambdaArn: migrateLambda.functionArn,
            CreateDbLambdaArn: createDbLambda.functionArn,
            DropDbLambdaArn: dropDbLambda.functionArn,
            CreateSuLambdaArn: createSuLambda.functionArn,
        };

        Object.entries(lambdaOutputs).forEach(([name, value]) => {
            outputs[name] = {
                value,
                description: `${name} Lambda function ARN`,
                exportName: stageConfig.getResourceName(name.toLowerCase()),
            };
        });

        // Add authorizer Lambda ARN output if it exists
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
