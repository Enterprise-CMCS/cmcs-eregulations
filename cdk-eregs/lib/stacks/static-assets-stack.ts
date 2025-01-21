import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as path from 'path';
import { execSync } from 'child_process';
import { StageConfig } from '../../config/stage-config';

export interface StaticAssetsStackProps extends cdk.StackProps {
  certificateArn?: string;
  prNumber?: string;
  // stageName: string;
}

export class StaticAssetsStack extends cdk.Stack {
  private readonly stageConfig: StageConfig;
  private readonly assetsBucket: s3.Bucket;
  private readonly loggingBucket: s3.Bucket;
  private readonly distribution: cloudfront.Distribution;

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

    this.deployStaticAssets(props.prNumber);
    this.addStackOutputs();
  }
  private validateCertificateConfig(props: StaticAssetsStackProps): void {
    if (this.stageConfig.environment === 'prod' && !props.certificateArn) {
      throw new Error('SSL Certificate ARN is required for production environment');
    }
  }
  private createAssetsBucket(): s3.Bucket {
    return new s3.Bucket(this, 'AssetsBucket', {
      bucketName: this.stageConfig.getResourceName(`site-assets`),
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      cors: [{
        allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
        allowedOrigins: ['*'],
        allowedHeaders: ['*'],
        maxAge: 3000,
      }],
    });
  }

  private createLoggingBucket(): s3.Bucket {
    return new s3.Bucket(this, 'CloudFrontLogsBucket', {
      bucketName: this.stageConfig.getResourceName('cloudfront-logs'),
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      enforceSSL: true,
      accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
    });
  }

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

  private runCollectStatic(prNumber?: string): void {
    const backendPath = path.join(__dirname, '../../../solution/backend');
    const staticRoot = '../static-assets/regulations';
    const staticUrl = `https://${this.distribution.domainName}/`;

    const env = {
      ...process.env,
      STATIC_URL: staticUrl,
      STATIC_ROOT: staticRoot,
      VITE_ENV: prNumber ? `dev${prNumber}` : 'prod',
    };

    try {
      console.log('Starting collectstatic with configuration:', {
        workingDirectory: backendPath,
        staticRoot,
        staticUrl,
        viteEnv: env.VITE_ENV,
      });

      execSync(`
        pushd ${backendPath} && \
        python3 manage.py collectstatic --noinput && \
        cd .. && \
        popd
      `, {
        stdio: 'inherit',
        shell: '/bin/bash',
        env,
        cwd: process.cwd(),
      });

      console.log('collectstatic completed successfully');
    } catch (error) {
      console.error('Error running collectstatic. Context:', {
        command: 'python manage.py collectstatic --noinput',
        workingDirectory: backendPath,
        currentDirectory: process.cwd(),
        nodeVersion: process.version,
        // Only log non-sensitive environment variables
        relevantEnvironment: {
          STATIC_URL: env.STATIC_URL,
          STATIC_ROOT: env.STATIC_ROOT,
          VITE_ENV: env.VITE_ENV,
        },
        error: error instanceof Error ? {
          message: error.message,
          stack: error.stack,
        } : error,
      });

      throw new Error(`Failed to run collectstatic: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private deployStaticAssets(prNumber?: string): void {
    this.runCollectStatic(prNumber);

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
