// // lib/stacks/static-assets-stack.ts

// import * as cdk from 'aws-cdk-lib';
// import * as s3 from 'aws-cdk-lib/aws-s3';
// import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
// import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
// import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
// import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
// import * as acm from 'aws-cdk-lib/aws-certificatemanager';
// import * as ssm from 'aws-cdk-lib/aws-ssm';
// import { Construct } from 'constructs';
// import { EnvironmentConfig } from '../../config/environment-config';

// interface StaticAssetsStackProps extends cdk.StackProps {
//   config: EnvironmentConfig;
// }

// export class StaticAssetsStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: StaticAssetsStackProps) {
//     super(scope, id, props);

//     const { config } = props;

//     // Create S3 bucket for static assets
//     const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
//       bucketName: `eregs-${config.stackPrefix}-site-assets`,
//       encryption: s3.BucketEncryption.S3_MANAGED,
//       publicReadAccess: false,
//       blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
//       cors: [
//         {
//           allowedHeaders: ['*'],
//           allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.HEAD],
//           allowedOrigins: ['*'],
//           maxAge: 3000,
//         },
//       ],
//     });

//     // Create S3 bucket for CloudFront logs
//     const logsBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
//       bucketName: `eregs-${config.stackPrefix}-cloudfront-logs`,
//       encryption: s3.BucketEncryption.S3_MANAGED,
//       publicReadAccess: false,
//       blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
//       objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
//       accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
//     });

//     // Create CloudFront Web ACL
//     const webAcl = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
//       name: `eregs-${config.stackPrefix}-cloudfront-ACL`,
//       defaultAction: { allow: {} },
//       scope: 'CLOUDFRONT',
//       visibilityConfig: {
//         cloudWatchMetricsEnabled: true,
//         metricName: `eregs-${config.stackPrefix}-cloudfront-metric`,
//         sampledRequestsEnabled: true,
//       },
//       rules: [
//         {
//           name: 'eregs-allow-usa-plus-territories-rule-cf',
//           priority: 0,
//           action: { allow: {} },
//           statement: {
//             geoMatchStatement: {
//               countryCodes: ['GU', 'PR', 'US', 'UM', 'VI', 'MP', 'AS'],
//             },
//           },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: 'eregs-allow-usa-plus-territories-metric-CLOUDFRONT',
//             sampledRequestsEnabled: true,
//           },
//         },
//       ],
//     });

//     // Retrieve ACM certificate ARN from SSM
//     const certificateArn = ssm.StringParameter.valueForStringParameter(
//       this,
//       '/eregulations/acm-cert-arn'
//     );

//     // Create CloudFront distribution
//     const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', {
//       defaultBehavior: {
//         origin: new origins.S3Origin(assetsBucket),
//         viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
//         allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
//         compress: true,
//       },
//       defaultRootObject: 'index.html',
//       httpVersion: cloudfront.HttpVersion.HTTP2,
//       enableLogging: true,
//       logBucket: logsBucket,
//       logFilePrefix: 'cf-logs/',
//       webAclId: webAcl.attrArn,
//       certificate: acm.Certificate.fromCertificateArn(this, 'Certificate', certificateArn),
//       minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
//     });

//     // Deploy static assets to S3
//     new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
//       sources: [s3deploy.Source.asset('../solution/static-assets/regulations')],
//       destinationBucket: assetsBucket,
//       distribution,
//       distributionPaths: ['/*'],
//     });

//     // Outputs
//     new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
//       value: distribution.distributionId,
//       description: 'CloudFront Distribution ID',
//     });

//     new cdk.CfnOutput(this, 'StaticURL', {
//       value: `https://${distribution.domainName}`,
//       description: 'Static Assets URL',
//     });
//   }
// }
// lib/stacks/static-asset-construct.ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import { Construct } from 'constructs';
import { SsmParameters } from '../../config/environment-config';

// Define the interface for StaticAssetsStack props
interface StaticAssetsStackProps extends cdk.StackProps {
  config: {
    stackPrefix: string;
    accountId: string;
    region: string;
    stage: string;
    isExperimental: boolean;
  };
  ssmParameters: SsmParameters;
}

export class StaticAssetsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: StaticAssetsStackProps) {
    super(scope, id, props);

    const { config, ssmParameters } = props;

    // Create S3 bucket for static assets
    const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
      bucketName: `eregs-${config.stackPrefix}-site-assets`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
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
      bucketName: `eregs-${config.stackPrefix}-cloudfront-logs`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
      accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
    });

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

    // Create CloudFront distribution with ACM certificate from SSM
    const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(assetsBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
        compress: true,
      },
      defaultRootObject: 'index.html',
      httpVersion: cloudfront.HttpVersion.HTTP2,
      enableLogging: true,
      logBucket: logsBucket,
      logFilePrefix: 'cf-logs/',
      webAclId: webAcl.attrArn,
      certificate: acm.Certificate.fromCertificateArn(
        this, 
        'Certificate', 
        ssmParameters.acmCertArn
      ),
      minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
    });

    // Deploy static assets to S3
    new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
      sources: [s3deploy.Source.asset('../solution/static-assets/regulations')],
      destinationBucket: assetsBucket,
      distribution,
      distributionPaths: ['/*'],
    });

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