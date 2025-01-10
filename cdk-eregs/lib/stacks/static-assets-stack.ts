import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import { StageConfig } from '../../config/stage-config';

/**
 * Properties for the StaticAssetsStack
 * @interface StaticAssetsStackProps
 * @extends cdk.StackProps
 */
export interface StaticAssetsStackProps extends cdk.StackProps {
  /** Optional ACM certificate ARN for CloudFront HTTPS */
  certificateArn?: string;
}

/**
 * AWS CDK Stack for managing static assets with CloudFront distribution
 * This stack creates:
 * - S3 bucket for static assets with proper security configurations
 * - CloudFront distribution with WAF protection
 * - Logging bucket for CloudFront
 * - Python Lambda layer for Django requirements
 * - Automated deployment of static assets
 * 
 * @example
 * ```typescript
 * const app = new cdk.App();
 * const stageConfig = new StageConfig({ stage: 'dev' });
 * 
 * new StaticAssetsStack(app, 'StaticAssets', {
 *   certificateArn: 'arn:aws:acm:...',  // optional
 * }, stageConfig);
 * ```
 */
export class StaticAssetsStack extends cdk.Stack {
  /** Stage-specific configuration for resource naming and tagging */
  private readonly stageConfig: StageConfig;

  /**
   * Creates a new StaticAssetsStack
   * @param scope - Parent construct
   * @param id - Stack identifier
   * @param props - Stack properties including optional certificate ARN
   * @param stageConfig - Stage-specific configuration
   */
  constructor(
    scope: Construct,
    id: string,
    props: StaticAssetsStackProps,
    stageConfig: StageConfig 
  ) {
    super(scope, id, props);

    this.stageConfig = stageConfig;
    const { certificateArn } = props;

    /**
     * S3 Bucket for storing static assets
     * - Blocks all public access
     * - Enables S3-managed encryption
     * - Configures CORS for GET/HEAD requests
     */
    const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
      bucketName: stageConfig.getResourceName('site-assets'),
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

    /**
     * S3 Bucket for CloudFront access logs
     * - Configures proper ownership and permissions for log delivery
     */
    const loggingBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
      bucketName: stageConfig.getResourceName('cloudfront-logs'),
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      enforceSSL: true,
      accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
    });

    /**
     * WAF configuration for CloudFront
     * - Restricts access to USA and territories
     * - Enables monitoring and metrics
     */
    const waf = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
      defaultAction: { allow: {} },
      scope: 'CLOUDFRONT',
      visibilityConfig: {
        sampledRequestsEnabled: true,
        cloudWatchMetricsEnabled: true,
        metricName: stageConfig.getResourceName('cloudfront-metric'),
      },
      name: stageConfig.getResourceName('cloudfront-acl'),
      rules: [
        {
          name: stageConfig.getResourceName('allow-usa-territories'),
          priority: 0,
          statement: {
            geoMatchStatement: {
              countryCodes: ['GU', 'PR', 'US', 'UM', 'VI', 'MP', 'AS'],
            },
          },
          action: { allow: {} },
          visibilityConfig: {
            sampledRequestsEnabled: true,
            cloudWatchMetricsEnabled: true,
            metricName: stageConfig.getResourceName('usa-territories-metric'),
          },
        },
      ],
    });

    /**
     * Lambda Layer containing Django requirements
     * Used by Lambda functions that need Django functionality
     */
    const pythonLayer = new lambda.LayerVersion(this, 'PythonDjangoLayer', {
      layerVersionName: stageConfig.getResourceName('python-django'),
      description: 'Layer which contains Django requirements',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/static-assets/regulations')),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
    });

    /**
     * CloudFront Distribution for serving static assets
     * - Configures S3 origin with Origin Access Control
     * - Enables HTTPS and modern security protocols
     * - Integrates with WAF and logging
     */
    const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(assetsBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
        compress: true,
      },
      comment: `CloudFront Distribution for ${this.stageConfig.getResourceName('site')}`,
      webAclId: waf.attrArn,
      logBucket: loggingBucket,
      logFilePrefix: 'cf-logs/',
      logIncludesCookies: false,
      defaultRootObject: 'index.html',
      httpVersion: cloudfront.HttpVersion.HTTP2,
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      domainNames: []
    });

    /**
     * Automated deployment of static assets to S3
     * - Excludes node_modules and nginx directories
     * - Invalidates CloudFront cache after deployment
     */
    new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
      sources: [
        s3deploy.Source.asset(path.join(__dirname, '../../../solution/static-assets/regulations'), {
          exclude: ['node_modules/**', 'nginx/**'],
        }),
      ],
      destinationBucket: assetsBucket,
      distribution,
      distributionPaths: ['/*'],
    });

    // Apply stage-specific tags to all resources
    Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });

    /**
     * Stack Outputs
     * - CloudFront Distribution ID for management
     * - Static assets URL for access
     * - Python Layer ARN for Lambda functions
     */
    new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
      value: distribution.distributionId,
      exportName: stageConfig.getResourceName('cloudfront-id'),
    });
    new cdk.CfnOutput(this, 'StaticURL', {
      value: `https://${distribution.domainName}`,
      exportName: stageConfig.getResourceName('static-url'),
    });
    new cdk.CfnOutput(this, 'PythonRequirementsLambdaLayerQualifiedArn', {
      value: pythonLayer.layerVersionArn,
      exportName: stageConfig.getResourceName('python-layer-arn'),
    });
  }
}


