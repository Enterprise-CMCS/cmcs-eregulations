import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as path from 'path';
import { StageConfig } from '../../config/stage-config';

/**
 * Properties for the StaticAssetsStack
 * @interface StaticAssetsStackProps
 * @extends {cdk.StackProps}
 */
export interface StaticAssetsStackProps extends cdk.StackProps {
    /** Optional ACM certificate ARN for custom domain */
    certificateArn?: string;
    /** Optional PR number for ephemeral environments */
    prNumber?: string;
    /** Type of deployment - either infrastructure setup or content deployment */
    deploymentType: 'infrastructure' | 'content';
}

/**
 * CDK Stack for managing static assets with CloudFront distribution
 * Creates and configures S3 buckets, CloudFront distribution, and WAF rules
 * @class StaticAssetsStack
 * @extends {cdk.Stack}
 */
export class StaticAssetsStack extends cdk.Stack {
    /**
     * Creates an instance of StaticAssetsStack
     * @param {Construct} scope - The scope in which to define this construct
     * @param {string} id - The scoped construct ID
     * @param {StaticAssetsStackProps} props - Configuration properties
     * @param {StageConfig} stageConfig - Stage-specific configuration
     */
    constructor(scope: Construct, id: string, props: StaticAssetsStackProps, stageConfig: StageConfig) {
        super(scope, id, props);

        const isEphemeral = stageConfig.isEphemeral();

        // =========================
        // SSL CERTIFICATE
        // =========================
        let certificateArn = props.certificateArn;
        if (!certificateArn) {
            certificateArn = ssm.StringParameter.valueFromLookup(this, '/eregulations/acm-cert-arn');
      
            if (certificateArn.startsWith('dummy-value-for-') || !certificateArn.startsWith('arn:aws:')) {
                // Use any valid ARN placeholder temporarily during synthesis
                certificateArn = 'arn:aws:acm:us-east-1:123456789012:certificate/dummy-placeholder';
            }
        }

        // =========================
        // S3 BUCKET
        // =========================
        const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
            bucketName: stageConfig.getResourceName('site-assets'),
            encryption: s3.BucketEncryption.S3_MANAGED,
            blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
            enforceSSL: true,
            autoDeleteObjects: isEphemeral,
            removalPolicy: isEphemeral ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN,      
            cors: [{
                allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                allowedOrigins: ['*'],
                allowedHeaders: ['*'],
                maxAge: 3000,
            }],
        });

        // ========================
        // LOGGING BUCKET
        // ========================
        const loggingBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
            bucketName: stageConfig.getResourceName('cloudfront-logs'),
            objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            enforceSSL: true,
            autoDeleteObjects: isEphemeral,
            removalPolicy: isEphemeral ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN,      
            accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
        });


        // ========================
        // WAF
        // ========================
        const waf = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
            defaultAction: { allow: {} },
            scope: 'CLOUDFRONT',
            visibilityConfig: {
                sampledRequestsEnabled: true,
                cloudWatchMetricsEnabled: true,
                metricName: stageConfig.getResourceName('cloudfront-metric'),
            },
            name: stageConfig.getResourceName('cloudfront-acl'),
            rules: [{
                name: stageConfig.getResourceName('allow-usa-territories'),
                priority: 0,
                statement: {
                    geoMatchStatement: {
                        countryCodes: ['US', 'GU', 'PR', 'VI', 'MP', 'AS', 'UM'],
                    },
                },
                action: { allow: {} },
                visibilityConfig: {
                    sampledRequestsEnabled: true,
                    cloudWatchMetricsEnabled: true,
                    metricName: stageConfig.getResourceName('usa-territories-metric'),
                },
            }],
        });

        // ========================
        // CLOUDFRONT DISTRIBUTION
        // ========================
        let distributionProps: cloudfront.DistributionProps = {
            defaultBehavior: {
                origin: origins.S3BucketOrigin.withOriginAccessControl(assetsBucket),
                viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                compress: true,
                cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD,
                cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
                originRequestPolicy: cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,
            },
            comment: `CloudFront Distribution for ${stageConfig.getResourceName('site')}`,
            webAclId: waf.attrArn,
            logBucket: loggingBucket,
            logFilePrefix: 'cf-logs/',
            logIncludesCookies: false,
            defaultRootObject: 'index.html',
            httpVersion: cloudfront.HttpVersion.HTTP2,
            minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            errorResponses: [
                {
                    httpStatus: 404,
                    responseHttpStatus: 404,
                    responsePagePath: '/404.html',
                    ttl: cdk.Duration.minutes(30),
                },
            ],
        };

        // Add certificate and domain configuration if certificate is available
        if (certificateArn) {
            // Create certificate reference
            const certificate = acm.Certificate.fromCertificateArn(
                this, 
                'Certificate', 
                certificateArn
            );
      
            // Include certificate in initial props
            distributionProps = {
                ...distributionProps,
                certificate,
                minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            };
        }

        // Create CloudFront distribution
        const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', distributionProps);

        // =========================
        // DEPLOY ASSETS
        // =========================
        // if (this.node.tryGetContext('deploymentType') === 'content') {
        //     new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
        //         sources: [
        //             s3deploy.Source.asset(path.join(__dirname, '../../../solution/static-assets/regulations')),
        //         ],
        //         destinationBucket: assetsBucket,
        //         distribution: distribution,
        //         distributionPaths: ['/*'],
        //     });
        // }
        new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
            sources: [
                s3deploy.Source.asset(path.join(__dirname, '../../../solution/static-assets/regulations')),
            ],
            destinationBucket: assetsBucket,
            distribution: distribution,
            distributionPaths: ['/*'],
        });

        // =========================
        // STACK OUTPUTS
        // =========================
        Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
            cdk.Tags.of(this).add(key, value);
        });

        new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
            value: distribution.distributionId,
            exportName: stageConfig.getResourceName('cloudfront-id'),
            description: 'CloudFront Distribution ID',
        });
    
        new cdk.CfnOutput(this, 'StaticURL', {
            value: `https://${distribution.domainName}`,
            exportName: stageConfig.getResourceName('static-url'),
            description: 'CloudFront Distribution URL',
        });
    }
}
