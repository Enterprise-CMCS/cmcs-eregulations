// #!/usr/bin/env node
// import * as cdk from 'aws-cdk-lib';
// import { getParameterValue } from '../utils/parameter-store';
// import { validateEnvironmentContext } from '../config/environment-config';
// import { RedirectApiStack } from '../lib/stacks/redirect-stack';
// import { StageConfig } from '../config/stage-config';
// import { IamPathAspect } from '../lib/aspects/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
// import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import { MaintenanceApiStack } from '../lib/stacks/maintainance-stack';
// import { TextExtractorStack } from '../lib/stacks/text-extract-stack';
// import { FrParserStack } from '../lib/stacks/fr-parser-stack';
// import { S3ImportStack } from '../lib/stacks/s3-import';
// import { EcfrParserStack } from '../lib/stacks/ecfr-parser-stack';

// // import { StackFactory } from '../lib/factories/stack-factory';
// // import { getStackConfigs } from '../config/stack-definition';
// async function main() {
//     // Initialize CDK App with synthesizer configuration
//     // const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
//     const synthesizerConfigJson = await getParameterValue('/eregulations/cdk_config');
//     const synthesizerConfig = JSON.parse(synthesizerConfigJson);
//     // Fetch all required SSM parameters
//     const [
//       vpcId,
//       logLevel,
//       httpUser,
//       httpPassword,
//       eregsApiUrl
//     ] = await Promise.all([
//       getParameterValue('/account_vars/vpc/id'),
//       getParameterValue('/eregulations/text_extractor/log_level'),
//       getParameterValue('/eregulations/http/user'),
//       getParameterValue('/eregulations/http/password'),
//       getParameterValue('/eregulations/custom_url'),
//     ]);

//      // Get environment configuration
//      const env = {
//       account: process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID,
//       region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
//     };
//     const app = new cdk.App({
//       defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(synthesizerConfig),
//     });
//     // Get bundling type from context
//     const bundlingType = app.node.tryGetContext('bundling');
//     const environment = app.node.tryGetContext('environment') ||
//   process.env.DEPLOY_ENV ||
//   process.env.GITHUB_JOB_ENVIRONMENT ||
//   'dev';
//   const prNumber = process.env.PR_NUMBER || '';
//   const ephemeralId = prNumber ? `eph-${prNumber}` : undefined;

//   const context = validateEnvironmentContext(
//     environment,
//     ephemeralId,
//     process.env.GITHUB_REF,
//     prNumber
//   );

//     // Debug logging for synthesizer config
//     if (process.env.CDK_DEBUG) {
//       console.log('Synthesizer Config:', {
//         permissionsBoundary: synthesizerConfig.iamPermissionsBoundary,
//         environment,
//         ephemeralId,
//       });
//     }


//   // const environment = process.env.DEPLOY_ENV || 'dev';


//   // Create StageConfig with synthesizer's permission boundary
//   const stageConfig = await StageConfig.create(
//     context.environment,
//     ephemeralId,
//     synthesizerConfig.iamPermissionsBoundary
//   );

//   // Debug logging for StageConfig
//   if (process.env.CDK_DEBUG) {
//     console.log('StageConfig Details:', {
//       environment: stageConfig.environment,
//       permissionsBoundary: stageConfig.permissionsBoundaryArn,
//       isEphemeral: stageConfig.isEphemeral(),
//       ephemeralId: ephemeralId,
//     });
//   }

//   // Set global tags
//   const tags = stageConfig.getStackTags();
//   Object.entries(tags).forEach(([key, value]) => {
//     cdk.Tags.of(app).add(key, value);
//   });

//   // Create RedirectApiStack
//  new RedirectApiStack(app, stageConfig.getResourceName('redirect-api'), {
//     lambdaConfig: {
//       runtime: lambda.Runtime.PYTHON_3_12,
//       memorySize: 1024,
//       timeout: 30,
//     },
//     apiConfig: {
//       loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
//     },
//   }, stageConfig);
//  new MaintenanceApiStack(app, stageConfig.getResourceName('maintenance-api'), {
//     lambdaConfig: {
//       runtime: lambda.Runtime.PYTHON_3_12,
//       memorySize: 1024,
//       timeout: 30,
//     },
//     apiConfig: {
//       loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
//     },
//   }, stageConfig);

//   new TextExtractorStack(app, stageConfig.getResourceName('text-extractor'), {
//     env,
//     lambdaConfig: {
//       memorySize: 1024,
//       timeout: 900,
//       reservedConcurrentExecutions: 10,
//     },
//     environmentConfig: {
//       vpcId,
//       logLevel,
//       httpUser,
//       httpPassword,
//     }
//   }, stageConfig);

//   new S3ImportStack(app, 'S3ImportStack', {
//     bucketName: process.env.BUCKET_NAME || '',
//     env: {
//       account: process.env.CDK_DEFAULT_ACCOUNT,
//       region: process.env.CDK_DEFAULT_REGION,
//     },
//   });

//   new FrParserStack(app, stageConfig.getResourceName('fr-parser'), {
//     env,
//     lambdaConfig: {
//       timeout: 900,
//     },
//     environmentConfig: {
//       vpcId,
//       logLevel,
//       httpUser,
//       httpPassword,
//     }
//   }, stageConfig);

//   new EcfrParserStack(app, stageConfig.getResourceName('ecfr-parser'), {
//     env,
//     lambdaConfig: {
//       timeout: 900,
//     },
//     environmentConfig: {
//       vpcId,
//       logLevel,
//       httpUser,
//       httpPassword,
//     }
//   }, stageConfig);

//   // Apply aspects
//   await applyGlobalAspects(app, stageConfig);

//   app.synth();
// }

// async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
//   const iamPath = await getParameterValue(`/account_vars/iam/path`);

//   // Apply IAM aspects using stageConfig's permission boundary
//   cdk.Aspects.of(app).add(new IamPathAspect(iamPath));
//   cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(stageConfig.permissionsBoundaryArn));
//   cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));

//   if (process.env.CDK_DEBUG) {
//     console.log('Applied Global Aspects:', {
//       environment: stageConfig.environment,
//       iamPath,
//       permissionsBoundary: stageConfig.permissionsBoundaryArn,
//       isEphemeral: stageConfig.isEphemeral(),
//     });
//   }
// }

// main().catch(error => {
//   console.error('Error initializing CDK app:', error);
//   process.exit(1);
// });

