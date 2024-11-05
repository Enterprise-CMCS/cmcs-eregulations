<<<<<<< HEAD


// lib/stacks/static-asset-construct.ts
=======
// lib/stacks/static-assets-stack.ts

>>>>>>> main
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
<<<<<<< HEAD
import { Construct } from 'constructs';
import { EnvironmentConfigStack } from '../../config/environment-config';

interface StaticAssetsStackProps extends cdk.StackProps {
  envStack: EnvironmentConfigStack;
=======
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { EnvironmentConfig } from '../../config/environment-config';

interface StaticAssetsStackProps extends cdk.StackProps {
  config: EnvironmentConfig;
>>>>>>> main
}

export class StaticAssetsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: StaticAssetsStackProps) {
    super(scope, id, props);

<<<<<<< HEAD
    const { envStack } = props;
    const { baseConfig, staticAssetsConfig } = envStack;

    // Create S3 bucket for static assets
    const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
      bucketName: staticAssetsConfig.bucketConfig.assetsBucketName,
      encryption: s3.BucketEncryption.S3_MANAGED,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioning: staticAssetsConfig.bucketConfig.versioning,
      lifecycleRules: staticAssetsConfig.bucketConfig.lifecycleRules.map(rule => ({
        enabled: rule.enabled,
        expiration: cdk.Duration.days(rule.expiration),
        noncurrentVersionExpiration: cdk.Duration.days(rule.noncurrentVersionExpiration),
      })),
=======
    const { config } = props;

    // Create S3 bucket for static assets
    const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
      bucketName: `eregs-${config.stackPrefix}-site-assets`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
>>>>>>> main
      cors: [
        {
          allowedHeaders: ['*'],
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
          allowedOrigins: ['*'],
          maxAge: 3000,
        },
      ],
    });

    // Create S3 bucket for CloudFront logs
    const logsBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
<<<<<<< HEAD
      bucketName: staticAssetsConfig.bucketConfig.logsBucketName,
=======
      bucketName: `eregs-${config.stackPrefix}-cloudfront-logs`,
>>>>>>> main
      encryption: s3.BucketEncryption.S3_MANAGED,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
    });

<<<<<<< HEAD
    // Create CloudFront Web ACL if WAF is enabled
    let webAcl: wafv2.CfnWebACL | undefined;
    
    if (staticAssetsConfig.waf.enabled) {
      webAcl = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
        name: `eregs-${baseConfig.stackPrefix}-cloudfront-ACL`,
        defaultAction: { allow: {} },
        scope: 'CLOUDFRONT',
        visibilityConfig: {
          cloudWatchMetricsEnabled: true,
          metricName: `eregs-${baseConfig.stackPrefix}-cloudfront-metric`,
          sampledRequestsEnabled: true,
        },
        rules: [
          {
            name: 'eregs-allow-usa-plus-territories-rule-cf',
            priority: 0,
            action: { allow: {} },
            statement: {
              geoMatchStatement: {
                countryCodes: staticAssetsConfig.allowedCountries,
              },
            },
            visibilityConfig: {
              cloudWatchMetricsEnabled: true,
              metricName: 'eregs-allow-usa-plus-territories-metric-CLOUDFRONT',
              sampledRequestsEnabled: true,
            },
          },
          // Add rate limiting rule if enabled
          ...(staticAssetsConfig.waf.ipRateLimiting.enabled ? [{
            name: 'ip-rate-limit',
            priority: 1,
            action: { block: {} },
            statement: {
              rateBasedStatement: {
                limit: staticAssetsConfig.waf.ipRateLimiting.limit,
                aggregateKeyType: 'IP',
              },
            },
            visibilityConfig: {
              cloudWatchMetricsEnabled: true,
              metricName: 'IPRateLimit',
              sampledRequestsEnabled: true,
            },
          }] : []),
        ],
      });
    }
=======
    // Create CloudFront Web ACL
    const webAcl = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
      name: `eregs-${config.stackPrefix}-cloudfront-ACL`,
      defaultAction: { allow: {} },
      scope: 'CLOUDFRONT',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: `eregs-${config.stackPrefix}-cloudfront-metric`,
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: 'eregs-allow-usa-plus-territories-rule-cf',
          priority: 0,
          action: { allow: {} },
          statement: {
            geoMatchStatement: {
              countryCodes: ['GU', 'PR', 'US', 'UM', 'VI', 'MP', 'AS'],
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'eregs-allow-usa-plus-territories-metric-CLOUDFRONT',
            sampledRequestsEnabled: true,
          },
        },
      ],
    });

    // Retrieve ACM certificate ARN from SSM
    const certificateArn = ssm.StringParameter.valueForStringParameter(
      this,
      '/eregulations/acm-cert-arn'
    );
>>>>>>> main

    // Create CloudFront distribution
    const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(assetsBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
<<<<<<< HEAD
        compress: staticAssetsConfig.distribution.enableCompression,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD,
        cachePolicyProps: {
          defaultTtl: cdk.Duration.seconds(staticAssetsConfig.distribution.defaultTtl),
          maxTtl: cdk.Duration.seconds(staticAssetsConfig.distribution.maxTtl),
          minTtl: cdk.Duration.seconds(staticAssetsConfig.distribution.minTtl),
        },
      },
      defaultRootObject: 'index.html',
      httpVersion: cloudfront.HttpVersion.HTTP2,
      enableLogging: staticAssetsConfig.distribution.enableLogging,
      logBucket: logsBucket,
      logFilePrefix: staticAssetsConfig.distribution.logFilePrefix,
      webAclId: webAcl?.attrArn,
      certificate: acm.Certificate.fromCertificateArn(
        this,
        'Certificate',
        staticAssetsConfig.acmCertArn
      ),
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
      priceClass: cloudfront.PriceClass[staticAssetsConfig.distribution.priceClass as keyof typeof cloudfront.PriceClass],
=======
        compress: true,
      },
      defaultRootObject: 'index.html',
      httpVersion: cloudfront.HttpVersion.HTTP2,
      enableLogging: true,
      logBucket: logsBucket,
      logFilePrefix: 'cf-logs/',
      webAclId: webAcl.attrArn,
      certificate: acm.Certificate.fromCertificateArn(this, 'Certificate', certificateArn),
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
>>>>>>> main
    });

    // Deploy static assets to S3
    new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
      sources: [s3deploy.Source.asset('../solution/static-assets/regulations')],
      destinationBucket: assetsBucket,
      distribution,
      distributionPaths: ['/*'],
    });

<<<<<<< HEAD
    // Add stack tags
    Object.entries(baseConfig.tags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });

=======
>>>>>>> main
    // Outputs
    new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
      value: distribution.distributionId,
      description: 'CloudFront Distribution ID',
    });

    new cdk.CfnOutput(this, 'StaticURL', {
      value: `https://${distribution.domainName}`,
      description: 'Static Assets URL',
    });
  }
}