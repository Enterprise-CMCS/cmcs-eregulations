import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as path from 'path';
import * as fs from 'fs-extra';
import { execSync } from 'child_process';
import { StageConfig } from '../../config/stage-config';

export interface StaticAssetsStackProps extends cdk.StackProps {
 requirementsPath?: string;
 layerVersionId?: string;
}

export class StaticAssetsStack extends cdk.Stack {
 private readonly stageConfig: StageConfig;
 public readonly pythonLayer: lambda.LayerVersion;
 private readonly layerVersionId: string;

 constructor(
   scope: Construct,
   id: string,
   props: StaticAssetsStackProps,
   stageConfig: StageConfig 
 ) {
   super(scope, id, props);

   this.stageConfig = stageConfig;
   this.layerVersionId = props.layerVersionId || this.generateVersionId(props.requirementsPath);
// Get ACM certificate ARN from SSM if it exists
    let certificateArn: string | undefined;
    try {
    certificateArn = ssm.StringParameter.valueFromLookup(
        this,
        '/eregulations/acm-cert-arn'
    );
    } catch (error) {
    console.log('No ACM certificate found in SSM, proceeding without custom domain');
    }

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

   const loggingBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
     bucketName: stageConfig.getResourceName('cloudfront-logs'),
     objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
     enforceSSL: true,
     accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
   });

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

   this.pythonLayer = this.createVersionedPythonLayer(props.requirementsPath);

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
     ...(certificateArn ? {
       viewerCertificate: cloudfront.ViewerCertificate.fromAcmCertificate(
         acm.Certificate.fromCertificateArn(this, 'Certificate', certificateArn),
         {
           securityPolicy: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
           aliases: [stageConfig.getResourceName('site-domain')]
         }
       )
     } : {}),
     enabled: true,
   });

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

   Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
     cdk.Tags.of(this).add(key, value);
   });

   this.exportStackOutputs(distribution);
   this.exportLayerArn();
 }

 private generateVersionId(requirementsPath?: string): string {
   const defaultRequirementsPath = path.join(__dirname, '../../../solution/static-assets/requirements.txt');
   const finalRequirementsPath = requirementsPath || defaultRequirementsPath;
   
   return fs.existsSync(finalRequirementsPath) 
     ? execSync(`sha256sum "${finalRequirementsPath}" | cut -d' ' -f1`).toString().trim().substring(0, 8)
     : 'default';
 }

 private createVersionedPythonLayer(requirementsPath?: string): lambda.LayerVersion {
   const defaultRequirementsPath = path.join(__dirname, '../../../solution/static-assets/requirements.txt');
   const finalRequirementsPath = requirementsPath || defaultRequirementsPath;
   const pythonRuntime = lambda.Runtime.PYTHON_3_12;
   const pythonVersion = pythonRuntime.name.replace('python', '');
   
   const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
   const outputDir = path.join(__dirname, `layer-output-${timestamp}`);
   const pythonDir = path.join(outputDir, 'python', 'lib', `python${pythonVersion}`, 'site-packages');
   const baseLayerName = this.stageConfig.getResourceName('python-django');
   const layerName = `${baseLayerName}-${this.layerVersionId}`;
   const zipFilePath = path.join(outputDir, `${layerName}.zip`);

   try {
     if (!fs.existsSync(finalRequirementsPath)) {
       throw new Error(`Requirements file not found: ${finalRequirementsPath}`);
     }

     fs.mkdirpSync(pythonDir);
     
     console.log('Installing Python packages...');
     execSync(`pip install -r "${finalRequirementsPath}" -t "${pythonDir}" --no-cache-dir`, {
       stdio: 'inherit',
       env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
     });

     if (!fs.existsSync(pythonDir) || fs.readdirSync(pythonDir).length === 0) {
       throw new Error(`Failed to install Python packages to: ${pythonDir}`);
     }

     console.log('Cleaning up unnecessary files...');
     execSync(`
       find "${outputDir}" -type d -name "__pycache__" -exec rm -rf {} +
       find "${outputDir}" -type f -name "*.pyc" -delete
       find "${outputDir}" -type f -name "*.pyo" -delete
       find "${outputDir}" -type d -name "tests" -exec rm -rf {} +
     `, { stdio: 'inherit' });

     console.log('Zipping Python packages...');
     execSync(`cd "${outputDir}" && zip -r "${zipFilePath}" .`, { stdio: 'inherit' });

     return new lambda.LayerVersion(this, layerName, {
       code: lambda.Code.fromAsset(zipFilePath),
       compatibleRuntimes: [pythonRuntime],
       description: `Django requirements layer (Version: ${this.layerVersionId})`,
       removalPolicy: cdk.RemovalPolicy.RETAIN,
     });

   } catch (error) {
     console.error('Error creating Lambda layer:', error);
     throw error;
   } finally {
     fs.removeSync(outputDir);
   }
 }

 private exportLayerArn() {
   // Keep the original export for backward compatibility
   new cdk.CfnOutput(this, 'PythonLayerArn', {
     value: this.pythonLayer.layerVersionArn,
     description: 'ARN of the Python Lambda Layer',
     exportName: this.stageConfig.getResourceName('python-layer-arn'),
   });

   // Add version identifier output
   new cdk.CfnOutput(this, 'PythonLayerVersion', {
     value: this.layerVersionId,
     description: 'Version identifier of the Python Lambda Layer',
     exportName: this.stageConfig.getResourceName('python-layer-version'),
   });

   // Add versioned ARN output
   new cdk.CfnOutput(this, 'PythonLayerVersionedArn', {
     value: this.pythonLayer.layerVersionArn,
     description: `ARN of the Python Lambda Layer (Version: ${this.layerVersionId})`,
     exportName: `${this.stageConfig.getResourceName('python-layer-arn')}-${this.layerVersionId}`,
   });
 }

 private exportStackOutputs(distribution: cloudfront.Distribution) {
   new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
     value: distribution.distributionId,
     exportName: this.stageConfig.getResourceName('cloudfront-id'),
   });

   new cdk.CfnOutput(this, 'StaticURL', {
     value: `https://${distribution.domainName}`,
     exportName: this.stageConfig.getResourceName('static-url'),
   });
 }
}
// import * as cdk from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import * as s3 from 'aws-cdk-lib/aws-s3';
// import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
// import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
// import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
// import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as path from 'path';
// import * as fs from 'fs-extra';
// import { execSync } from 'child_process';
// import { StageConfig } from '../../config/stage-config';

// /**
//  * Properties for the StaticAssetsStack
//  * @interface StaticAssetsStackProps
//  * @extends cdk.StackProps
//  */
// export interface StaticAssetsStackProps extends cdk.StackProps {
//   /** Optional ACM certificate ARN for CloudFront HTTPS */
//   certificateArn?: string;
//   /** Optional path to requirements.txt */
//   requirementsPath?: string;
// }

// /**
//  * AWS CDK Stack for managing static assets with CloudFront distribution
//  * This stack creates:
//  * - S3 bucket for static assets with proper security configurations
//  * - CloudFront distribution with WAF protection
//  * - Logging bucket for CloudFront
//  * - Python Lambda layer for Django requirements
//  * - Automated deployment of static assets
//  * 
//  * @example
//  * ```typescript
//  * const app = new cdk.App();
//  * const stageConfig = new StageConfig({ stage: 'dev' });
//  * 
//  * new StaticAssetsStack(app, 'StaticAssets', {
//  *   certificateArn: 'arn:aws:acm:...',  // optional
//  * }, stageConfig);
//  * ```
//  */
// export class StaticAssetsStack extends cdk.Stack {
//   /** Stage-specific configuration for resource naming and tagging */
//   private readonly stageConfig: StageConfig;

//   /**
//    * Creates a new StaticAssetsStack
//    * @param scope - Parent construct
//    * @param id - Stack identifier
//    * @param props - Stack properties including optional certificate ARN
//    * @param stageConfig - Stage-specific configuration
//    */
//   constructor(
//     scope: Construct,
//     id: string,
//     props: StaticAssetsStackProps,
//     stageConfig: StageConfig 
//   ) {
//     super(scope, id, props);

//     this.stageConfig = stageConfig;
//     const { certificateArn, requirementsPath } = props;

//     /**
//      * S3 Bucket for storing static assets
//      * - Blocks all public access
//      * - Enables S3-managed encryption
//      * - Configures CORS for GET/HEAD requests
//      */
//     const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
//       bucketName: stageConfig.getResourceName('site-assets'),
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

//     /**
//      * S3 Bucket for CloudFront access logs
//      * - Configures proper ownership and permissions for log delivery
//      */
//     const loggingBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
//       bucketName: stageConfig.getResourceName('cloudfront-logs'),
//       objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
//       enforceSSL: true,
//       accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
//     });

//     /**
//      * WAF configuration for CloudFront
//      * - Restricts access to USA and territories
//      * - Enables monitoring and metrics
//      */
//     const waf = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
//       defaultAction: { allow: {} },
//       scope: 'CLOUDFRONT',
//       visibilityConfig: {
//         sampledRequestsEnabled: true,
//         cloudWatchMetricsEnabled: true,
//         metricName: stageConfig.getResourceName('cloudfront-metric'),
//       },
//       name: stageConfig.getResourceName('cloudfront-acl'),
//       rules: [
//         {
//           name: stageConfig.getResourceName('allow-usa-territories'),
//           priority: 0,
//           statement: {
//             geoMatchStatement: {
//               countryCodes: ['GU', 'PR', 'US', 'UM', 'VI', 'MP', 'AS'],
//             },
//           },
//           action: { allow: {} },
//           visibilityConfig: {
//             sampledRequestsEnabled: true,
//             cloudWatchMetricsEnabled: true,
//             metricName: stageConfig.getResourceName('usa-territories-metric'),
//           },
//         },
//       ],
//     });

//     /**
//      * Lambda Layer containing Django requirements
//      * Used by Lambda functions that need Django functionality
//      */
//     const pythonLayer = this.createPythonDjangoLayer(requirementsPath);

//     /**
//      * CloudFront Distribution for serving static assets
//      * - Configures S3 origin with Origin Access Control
//      * - Enables HTTPS and modern security protocols
//      * - Integrates with WAF and logging
//      */
//     const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', {
//       defaultBehavior: {
//         origin: origins.S3BucketOrigin.withOriginAccessControl(assetsBucket),
//         viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
//         allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
//         compress: true,
//       },
//       comment: `CloudFront Distribution for ${this.stageConfig.getResourceName('site')}`,
//       webAclId: waf.attrArn,
//       logBucket: loggingBucket,
//       logFilePrefix: 'cf-logs/',
//       logIncludesCookies: false,
//       defaultRootObject: 'index.html',
//       httpVersion: cloudfront.HttpVersion.HTTP2,
//       minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
//       domainNames: []
//     });

//     /**
//      * Automated deployment of static assets to S3
//      * - Excludes node_modules and nginx directories
//      * - Invalidates CloudFront cache after deployment
//      */
//     new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
//       sources: [
//         s3deploy.Source.asset(path.join(__dirname, '../../../solution/static-assets/regulations'), {
//           exclude: ['node_modules/**', 'nginx/**'],
//         }),
//       ],
//       destinationBucket: assetsBucket,
//       distribution,
//       distributionPaths: ['/*'],
//     });

//     // Apply stage-specific tags to all resources
//     Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
//       cdk.Tags.of(this).add(key, value);
//     });

//     /**
//      * Stack Outputs
//      * - CloudFront Distribution ID for management
//      * - Static assets URL for access
//      * - Python Layer ARN for Lambda functions
//      */
//     new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
//       value: distribution.distributionId,
//       exportName: stageConfig.getResourceName('cloudfront-id'),
//     });
//     new cdk.CfnOutput(this, 'StaticURL', {
//       value: `https://${distribution.domainName}`,
//       exportName: stageConfig.getResourceName('static-url'),
//     });
//     new cdk.CfnOutput(this, 'PythonRequirementsLambdaLayerQualifiedArn', {
//       value: pythonLayer.layerVersionArn,
//       exportName: stageConfig.getResourceName('python-layer-arn'),
//     });
//   }

//   /**
//    * Creates a Python Lambda Layer with robust package installation
//    * @param requirementsPath Optional path to requirements.txt
//    * @returns Lambda Layer with installed dependencies
//    */
//   private createPythonDjangoLayer(requirementsPath?: string): lambda.LayerVersion {
//     // Default to a path relative to the current directory
//     const defaultRequirementsPath = path.join(__dirname, '../../../solution/static-assets/requirements.txt');
//     const finalRequirementsPath = requirementsPath || defaultRequirementsPath;

//     // Determine Python version dynamically
//     const pythonRuntime = lambda.Runtime.PYTHON_3_12;
//     const pythonVersion = pythonRuntime.name.replace('python', '');

//     // Define paths with unique identifier to prevent conflicts
//     const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
//     const outputDir = path.join(__dirname, `layer-output-${timestamp}`);
//     const pythonDir = path.join(outputDir, 'python', 'lib', `python${pythonVersion}`, 'site-packages');
//     const layerName = this.stageConfig.getResourceName('python-django');
//     const zipFilePath = path.join(outputDir, `${layerName}.zip`);

//     try {
//       // Validate requirements file
//       if (!fs.existsSync(finalRequirementsPath)) {
//         throw new Error(`Requirements file not found: ${finalRequirementsPath}`);
//       }

//       // Create output directories
//       fs.mkdirpSync(pythonDir);

//       // Install dependencies
//       console.log('Installing Python packages...');
//       execSync(`pip install -r "${finalRequirementsPath}" -t "${pythonDir}" --no-cache-dir`, { 
//         stdio: 'inherit',
//         env: { ...process.env, PIP_DISABLE_PIP_VERSION_CHECK: '1' }
//       });

//       // Validate installation
//       if (!fs.existsSync(pythonDir) || fs.readdirSync(pythonDir).length === 0) {
//         throw new Error(`Failed to install Python packages to: ${pythonDir}`);
//       }

//       // Cleanup unnecessary files
//       console.log('Cleaning up unnecessary files...');
//       execSync(`
//         find "${outputDir}" -type d -name "__pycache__" -exec rm -rf {} +
//         find "${outputDir}" -type f -name "*.pyc" -delete
//         find "${outputDir}" -type f -name "*.pyo" -delete
//         find "${outputDir}" -type d -name "tests" -exec rm -rf {} +
//       `, { stdio: 'inherit' });

//       // Create zip file
//       console.log('Zipping Python packages...');
//       execSync(`cd "${outputDir}" && zip -r "${zipFilePath}" .`, { stdio: 'inherit' });

//       // Create the Lambda layer
//       return new lambda.LayerVersion(this, 'PythonDjangoLayer', {
//         layerVersionName: layerName,
//         description: 'Layer which contains Django requirements',
//         code: lambda.Code.fromAsset(zipFilePath),
//         compatibleRuntimes: [pythonRuntime],
//         removalPolicy: cdk.RemovalPolicy.DESTROY,
//       });

//     } catch (error) {
//       console.error('Error creating Lambda layer:', error);
//       throw error;
//     } finally {
//       // Optional: Uncomment to clean up output directory after use
//       // fs.removeSync(outputDir);
//     }
//   }
// }

// import * as cdk from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import * as s3 from 'aws-cdk-lib/aws-s3';
// import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
// import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
// import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
// import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as path from 'path';
// import { StageConfig } from '../../config/stage-config';

// /**
//  * Properties for the StaticAssetsStack
//  * @interface StaticAssetsStackProps
//  * @extends cdk.StackProps
//  */
// export interface StaticAssetsStackProps extends cdk.StackProps {
//   /** Optional ACM certificate ARN for CloudFront HTTPS */
//   certificateArn?: string;
// }

// /**
//  * AWS CDK Stack for managing static assets with CloudFront distribution
//  * This stack creates:
//  * - S3 bucket for static assets with proper security configurations
//  * - CloudFront distribution with WAF protection
//  * - Logging bucket for CloudFront
//  * - Python Lambda layer for Django requirements
//  * - Automated deployment of static assets
//  * 
//  * @example
//  * ```typescript
//  * const app = new cdk.App();
//  * const stageConfig = new StageConfig({ stage: 'dev' });
//  * 
//  * new StaticAssetsStack(app, 'StaticAssets', {
//  *   certificateArn: 'arn:aws:acm:...',  // optional
//  * }, stageConfig);
//  * ```
//  */
// export class StaticAssetsStack extends cdk.Stack {
//   /** Stage-specific configuration for resource naming and tagging */
//   private readonly stageConfig: StageConfig;

//   /**
//    * Creates a new StaticAssetsStack
//    * @param scope - Parent construct
//    * @param id - Stack identifier
//    * @param props - Stack properties including optional certificate ARN
//    * @param stageConfig - Stage-specific configuration
//    */
//   constructor(
//     scope: Construct,
//     id: string,
//     props: StaticAssetsStackProps,
//     stageConfig: StageConfig 
//   ) {
//     super(scope, id, props);

//     this.stageConfig = stageConfig;
//     const { certificateArn } = props;

//     /**
//      * S3 Bucket for storing static assets
//      * - Blocks all public access
//      * - Enables S3-managed encryption
//      * - Configures CORS for GET/HEAD requests
//      */
//     const assetsBucket = new s3.Bucket(this, 'AssetsBucket', {
//       bucketName: stageConfig.getResourceName('site-assets'),
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

//     /**
//      * S3 Bucket for CloudFront access logs
//      * - Configures proper ownership and permissions for log delivery
//      */
//     const loggingBucket = new s3.Bucket(this, 'CloudFrontLogsBucket', {
//       bucketName: stageConfig.getResourceName('cloudfront-logs'),
//       objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
//       enforceSSL: true,
//       accessControl: s3.BucketAccessControl.LOG_DELIVERY_WRITE,
//     });

//     /**
//      * WAF configuration for CloudFront
//      * - Restricts access to USA and territories
//      * - Enables monitoring and metrics
//      */
//     const waf = new wafv2.CfnWebACL(this, 'CloudFrontWebACL', {
//       defaultAction: { allow: {} },
//       scope: 'CLOUDFRONT',
//       visibilityConfig: {
//         sampledRequestsEnabled: true,
//         cloudWatchMetricsEnabled: true,
//         metricName: stageConfig.getResourceName('cloudfront-metric'),
//       },
//       name: stageConfig.getResourceName('cloudfront-acl'),
//       rules: [
//         {
//           name: stageConfig.getResourceName('allow-usa-territories'),
//           priority: 0,
//           statement: {
//             geoMatchStatement: {
//               countryCodes: ['GU', 'PR', 'US', 'UM', 'VI', 'MP', 'AS'],
//             },
//           },
//           action: { allow: {} },
//           visibilityConfig: {
//             sampledRequestsEnabled: true,
//             cloudWatchMetricsEnabled: true,
//             metricName: stageConfig.getResourceName('usa-territories-metric'),
//           },
//         },
//       ],
//     });

//     /**
//      * Lambda Layer containing Django requirements
//      * Used by Lambda functions that need Django functionality
//      */
//     const pythonLayer = new lambda.LayerVersion(this, 'PythonDjangoLayer', {
//       layerVersionName: stageConfig.getResourceName('python-django'),
//       description: 'Layer which contains Django requirements',
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/static-assets/regulations')),
//       compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
//     });

//     /**
//      * CloudFront Distribution for serving static assets
//      * - Configures S3 origin with Origin Access Control
//      * - Enables HTTPS and modern security protocols
//      * - Integrates with WAF and logging
//      */
//     const distribution = new cloudfront.Distribution(this, 'CloudFrontDistribution', {
//       defaultBehavior: {
//         origin: origins.S3BucketOrigin.withOriginAccessControl(assetsBucket),
//         viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
//         allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
//         compress: true,
//       },
//       comment: `CloudFront Distribution for ${this.stageConfig.getResourceName('site')}`,
//       webAclId: waf.attrArn,
//       logBucket: loggingBucket,
//       logFilePrefix: 'cf-logs/',
//       logIncludesCookies: false,
//       defaultRootObject: 'index.html',
//       httpVersion: cloudfront.HttpVersion.HTTP2,
//       minimumProtocolVersion: cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
//       domainNames: []
//     });

//     /**
//      * Automated deployment of static assets to S3
//      * - Excludes node_modules and nginx directories
//      * - Invalidates CloudFront cache after deployment
//      */
//     new s3deploy.BucketDeployment(this, 'DeployStaticAssets', {
//       sources: [
//         s3deploy.Source.asset(path.join(__dirname, '../../../solution/static-assets/regulations'), {
//           exclude: ['node_modules/**', 'nginx/**'],
//         }),
//       ],
//       destinationBucket: assetsBucket,
//       distribution,
//       distributionPaths: ['/*'],
//     });

//     // Apply stage-specific tags to all resources
//     Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
//       cdk.Tags.of(this).add(key, value);
//     });

//     /**
//      * Stack Outputs
//      * - CloudFront Distribution ID for management
//      * - Static assets URL for access
//      * - Python Layer ARN for Lambda functions
//      */
//     new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
//       value: distribution.distributionId,
//       exportName: stageConfig.getResourceName('cloudfront-id'),
//     });
//     new cdk.CfnOutput(this, 'StaticURL', {
//       value: `https://${distribution.domainName}`,
//       exportName: stageConfig.getResourceName('static-url'),
//     });
//     new cdk.CfnOutput(this, 'PythonRequirementsLambdaLayerQualifiedArn', {
//       value: pythonLayer.layerVersionArn,
//       exportName: stageConfig.getResourceName('python-layer-arn'),
//     });
//   }
// }


