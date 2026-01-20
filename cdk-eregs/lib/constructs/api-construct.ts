import * as cdk from 'aws-cdk-lib';
import {
    aws_ec2 as ec2,
    aws_lambda as lambda,
    aws_apigateway as apigateway,
    aws_logs as logs,
    aws_iam as iam,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

/**
* Properties for the API Gateway construct
* @interface ApiConstructProps
*/
export interface ApiConstructProps {
    /** VPC configuration */
    vpc: ec2.IVpc;
    /** Security group for API resources */
    securityGroup: ec2.ISecurityGroup;
    /** Environment variables for Lambda functions */
    environmentVariables: Record<string, string>;
    /** Name of the S3 bucket for storage */
    storageBucketName: string;
    /** URL of the SQS queue */
    queueUrl: string;
    /** Configuration for Lambda functions */
    lambdaConfig: {
        /** Memory size in MB */
        memorySize: number;
        /** Timeout in seconds */
        timeout: number;
        /** Optional concurrent execution limit */
        reservedConcurrentExecutions?: number;
    };
    /** Stage configuration */
    stageConfig: StageConfig;
    /** VPC subnet selection */
    vpcSubnets: ec2.SubnetSelection;
    /** Main Lambda function for API */
    lambda: lambda.Function;
    /** Optional authorizer Lambda function */
    authorizerLambda?: lambda.Function;
}

/**
* Construct that creates an API Gateway with Lambda integration and optional authorization
* @class ApiConstruct
*/
export class ApiConstruct extends Construct {
    /** The created API Gateway REST API */
    public readonly api: apigateway.RestApi;
    /** The main Lambda function */
    public readonly lambda: lambda.Function;

    /**
    * Creates a new API Gateway construct
    * @param {Construct} scope - The parent construct
    * @param {string} id - The construct's unique id
    * @param {ApiConstructProps} props - Configuration properties
    */
    constructor(scope: Construct, id: string, props: ApiConstructProps) {
        super(scope, id);

        this.lambda = props.lambda;

        // Create API Gateway log group
        const apiLogGroup = new logs.LogGroup(this, 'ApiGatewayLogGroup', {
            logGroupName: props.stageConfig.aws.apiGateway('api'),
            retention: logs.RetentionDays.ONE_MONTH,
        });

        // Determine stage name based on environment type
        const stageName = props.stageConfig.isEphemeral() 
            ? props.stageConfig.getResourceName('')
                .replace(`${StageConfig.projectName}-`, '')
                .split('-resource')[0]
                .replace(/-$/, '')
            : props.stageConfig.environment;

        // Create API Gateway
        this.api = new apigateway.RestApi(this, 'API', {
            deploy: false,
            restApiName: props.stageConfig.getResourceName('api'),
            description: 'eRegulations API Gateway',
            deployOptions: {
                stageName: stageName,
                loggingLevel: apigateway.MethodLoggingLevel.INFO,
                dataTraceEnabled: true,
                accessLogDestination: new apigateway.LogGroupLogDestination(apiLogGroup),
                accessLogFormat: apigateway.AccessLogFormat.clf(),
                metricsEnabled: true,
                tracingEnabled: true,
            },
            binaryMediaTypes: [
                'multipart/form-data',
                'application/pdf',
                'application/json',
                'application/octet-stream',
                'image/*',
            ],
        });

        // Create request authorizer if Lambda is provided (non-prod environments)
        let authorizer: apigateway.IAuthorizer | undefined;
        if (props.authorizerLambda) {
            authorizer = new apigateway.RequestAuthorizer(this, 'ApiGatewayAuthorizer', {
                handler: props.authorizerLambda,
                identitySources: [apigateway.IdentitySource.header('Authorization')],
                authorizerName: props.stageConfig.getResourceName('authorizer'),
                resultsCacheTtl: cdk.Duration.seconds(0),
            });

            // Grant API Gateway permission to invoke the authorizer
            props.authorizerLambda.addPermission('ApiGatewayInvoke', {
                principal: new iam.ServicePrincipal('apigateway.amazonaws.com'),
                sourceArn: cdk.Fn.join(':', [
                    'arn:aws:execute-api',
                    cdk.Stack.of(this).region,
                    cdk.Stack.of(this).account,
                    `${this.api.restApiId}/authorizers/*`
                ])
            });

            // Set environment variables for the authorizer
            props.authorizerLambda.addEnvironment('HTTP_AUTH_USER', props.environmentVariables.HTTP_AUTH_USER);
            props.authorizerLambda.addEnvironment('HTTP_AUTH_PASSWORD', props.environmentVariables.HTTP_AUTH_PASSWORD);
        }

        // Create Lambda integration
        const integration = new apigateway.LambdaIntegration(this.lambda, {
            proxy: true,
            allowTestInvoke: true,
        });

        // Configure method options
        const methodOptions: apigateway.MethodOptions = {
            apiKeyRequired: false,
            authorizer: authorizer,
            authorizationType: props.authorizerLambda 
                ? apigateway.AuthorizationType.CUSTOM 
                : apigateway.AuthorizationType.NONE,
        };

        // Add API methods
        this.api.root.addMethod('ANY', integration, methodOptions);

        // Add proxy for all other routes
        this.api.root.addProxy({
            defaultIntegration: integration,
            defaultMethodOptions: methodOptions,
            anyMethod: true,
        });

        // Add unauthorized response configuration
        new apigateway.GatewayResponse(this, 'UnauthorizedResponse', {
            restApi: this.api,
            type: apigateway.ResponseType.UNAUTHORIZED,
            responseHeaders: {
                'gatewayresponse.header.WWW-Authenticate': "'Basic'",
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'",
            },
            statusCode: '401',
        });

        // Add CORS configuration
        this.addCorsOptions(this.api.root);

        // Force a deployment
        // Use a context variable to force deployment
        const forceDeploy = cdk.Stack.of(this).node.tryGetContext('forceDeploy') || 'none';
        // Deployment logical ID changes with forceDeploy, Stage logical ID is stable
        const deployment = new apigateway.Deployment(this, `ApiDeployment${forceDeploy}`, {
            api: this.api,
            description: `Force deployment: ${forceDeploy}`,
        });
        deployment.node.addDependency(this.api.methods[0]);

        // Stage logical ID is stable so it is updated, not replaced
        new apigateway.Stage(this, 'ApiStage', {
            deployment,
            stageName: stageName,
        });
    }

    /**
    * Adds CORS options to an API resource
    * @param {apigateway.IResource} apiResource - The API resource to add CORS options to
    * @private
    */
    private addCorsOptions(apiResource: apigateway.IResource) {
        apiResource.addMethod(
            'OPTIONS',
            new apigateway.MockIntegration({
                integrationResponses: [
                    {
                        statusCode: '200',
                        responseParameters: {
                            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'",
                            'method.response.header.Access-Control-Allow-Origin': "'*'",
                            'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET,PUT,POST,DELETE,PATCH,HEAD'",
                        },
                    },
                ],
                passthroughBehavior: apigateway.PassthroughBehavior.NEVER,
                requestTemplates: {
                    'application/json': '{"statusCode": 200}',
                },
            }),
            {
                methodResponses: [
                    {
                        statusCode: '200',
                        responseParameters: {
                            'method.response.header.Access-Control-Allow-Headers': true,
                            'method.response.header.Access-Control-Allow-Methods': true,
                            'method.response.header.Access-Control-Allow-Origin': true,
                        },
                    },
                ],
            }
        );
    }
}
