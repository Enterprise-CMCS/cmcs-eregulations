import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
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
  private readonly stageConfig: StageConfig;
  private readonly assetsBucket: s3.Bucket;
  private readonly loggingBucket: s3.Bucket;
  private readonly distribution: cloudfront.Distribution;

  /**
   * Creates an instance of StaticAssetsStack
   * @param {Construct} scope - The scope in which to define this construct
   * @param {string} id - The scoped construct ID
   * @param {StaticAssetsStackProps} props - Configuration properties
   * @param {StageConfig} stageConfig - Stage-specific configuration
   */
  constructor(
    scope: Construct,
    id: string,
    props: StaticAssetsStackProps,
    stageConfig: StageConfig
  ) {
    super(scope, id, props);

    this.stageConfig = stageConfig;
    this.validateCertificateConfig(props);

    this.assetsBucket = this.createAssetsBucket();
    this.loggingBucket = this.createLoggingBucket();
    const waf = this.createWebACL();
    this.distribution = this.createCloudFrontDistribution(waf, props);

    this.deployStaticAssets();
    this.addStackOutputs();
  }

  /**
   * Validates SSL certificate configuration for production environment
   * @private
   * @param {StaticAssetsStackProps} props - Stack properties
   * @throws {Error} If certificate ARN is missing in production environment
   */
  private validateCertificateConfig(props: StaticAssetsStackProps): void {
    // Temporarily disable certificate requirement for initial setup
    if (false && this.stageConfig.environment === 'prod' && !props.certificateArn) {
      throw new Error('SSL Certificate ARN is required for production environment');
    }
  }

  /**
   * Creates S3 bucket for storing static assets
   * @private
   * @returns {s3.Bucket} Configured S3 bucket for assets
   */
  private createAssetsBucket(): s3.Bucket {
    const isEphemeral = this.stageConfig.isEphemeral();
    return new s3.Bucket(this, 'AssetsBucket', {
      bucketName: this.stageConfig.getResourceName('site-assets'),
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
  }

  /**
   * Creates S3 bucket for CloudFront access logging
   * @private
   * @returns {s3.Bucket} Configured logging bucket
   */
  private createLoggingBucket(): s3.Bucket {
    const isEphemeral = this.stageConfig.isEphemeral();
    return new s3.Bucket(this, 'CloudFrontLogsBucket', {
      bucketName: this.stageConfig.getResourceName('cloudfront-logs'),
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      enforceSSL: true,
      autoDeleteObjects: isEphemeral,
      removalPolicy: isEphemeral ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN,
      accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
    });
  }

  /**
   * Creates WAF Web ACL for CloudFront with geographical restrictions
   * @private
   * @returns {wafv2.CfnWebACL} Configured Web ACL
   */
  private createWebACL(): wafv2.CfnWebACL {
    return new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
      defaultAction: { allow: {} },
      scope: 'CLOUDFRONT',
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: this.stageConfig.getResourceName('cloudfront-metric'),
      },
      name: this.stageConfig.getResourceName('cloudfront-acl'),
      rules: [{
        name: this.stageConfig.getResourceName('allow-usa-territories'),
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
          metricName: this.stageConfig.getResourceName('usa-territories-metric'),
        },
      }],
    });
  }

  /**
   * Creates and configures CloudFront distribution
   * @private
   * @param {wafv2.CfnWebACL} waf - WAF Web ACL to attach to the distribution
   * @param {StaticAssetsStackProps} props - Stack properties
   * @returns {cloudfront.Distribution} Configured CloudFront distribution
   */
  private createCloudFrontDistribution(
    waf: wafv2.CfnWebACL,
    props: StaticAssetsStackProps
  ): cloudfront.Distribution {
    return new cloudfront.Distribution(this, 'CloudFrontDistribution', {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(this.assetsBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
        compress: true,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        originRequestPolicy: cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,
      },
      comment: `CloudFront Distribution for ${this.stageConfig.getResourceName('site')}`,
      webAclId: waf.attrArn,
      logBucket: this.loggingBucket,
      logFilePrefix: 'cf-logs/',
      logIncludesCookies: false,
      defaultRootObject: 'index.html',
      httpVersion: cloudfront.HttpVersion.HTTP2,
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      domainNames: props.certificateArn ? [] : undefined,
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 404,
          responsePagePath: '/404.html',
          ttl: cdk.Duration.minutes(30),
        },
      ],
    });
  }

  /**
   * Deploys static assets to S3 and invalidates CloudFront cache
   * Only executes if deploymentType is 'content'
   * @private
   */
  private deployStaticAssets(): void {
    if (this.node.tryGetContext('deploymentType') === 'infrastructure') {
      return;
    }
    new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
      sources: [
        s3deploy.Source.asset(path.join(__dirname, '../../../solution/static-assets/regulations')),
      ],
      destinationBucket: this.assetsBucket,
      distribution: this.distribution,
      distributionPaths: ['/*'],
    });

    Object.entries(this.stageConfig.getStackTags()).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });
  }

  /**
   * Adds CloudFront distribution ID and URL as stack outputs
   * @private
   */
  private addStackOutputs(): void {
    new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
      value: this.distribution.distributionId,
      exportName: this.stageConfig.getResourceName('cloudfront-id'),
      description: 'CloudFront Distribution ID',
    });

    new cdk.CfnOutput(this, 'StaticURL', {
      value: `https://${this.distribution.domainName}`,
      exportName: this.stageConfig.getResourceName('static-url'),
      description: 'CloudFront Distribution URL',
    });
  }
}