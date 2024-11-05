#!/usr/bin/env node
<<<<<<< HEAD
import * as cdk from 'aws-cdk-lib';
import { getParameterValue } from '../utils/parameter-store';
import { validateEnvironmentContext } from '../config/environment-config';
import { RedirectApiStack } from '../lib/stacks/redirect-stack';
import { StageConfig } from '../config/stage-config';
import { IamPathAspect } from '../lib/aspects/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { StackFactory } from '../lib/factories/stack-factory';
import { getStackConfigs } from '../config/stack-definition';
async function main() {
    // Initialize CDK App with synthesizer configuration
    const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
    const synthesizerConfig = JSON.parse(synthesizerConfigJson);
    const app = new cdk.App({
      defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(synthesizerConfig),
    });
  
    const environment = app.node.tryGetContext('environment') || 
  process.env.DEPLOY_ENV || 
  process.env.GITHUB_JOB_ENVIRONMENT || 
  'dev';
  const prNumber = process.env.PR_NUMBER || '';
  const ephemeralId = prNumber ? `eph-${prNumber}` : undefined;

  const context = validateEnvironmentContext(
    environment,
    ephemeralId,
    process.env.GITHUB_REF,
    prNumber
  );

    // Debug logging for synthesizer config
    if (process.env.CDK_DEBUG) {
      console.log('Synthesizer Config:', {
        permissionsBoundary: synthesizerConfig.iamPermissionsBoundary,
        environment,
        ephemeralId,
      });
    }
  

  // const environment = process.env.DEPLOY_ENV || 'dev';


  // Create StageConfig with synthesizer's permission boundary
  const stageConfig = await StageConfig.create(
    context.environment,
    ephemeralId,
    synthesizerConfig.iamPermissionsBoundary
  );

  // Debug logging for StageConfig
  if (process.env.CDK_DEBUG) {
    console.log('StageConfig Details:', {
      environment: stageConfig.environment,
      permissionsBoundary: stageConfig.permissionsBoundaryArn,
      isEphemeral: stageConfig.isEphemeral(),
      ephemeralId: ephemeralId,
    });
  }

  // Set global tags
  const tags = stageConfig.getStackTags();
  Object.entries(tags).forEach(([key, value]) => {
    cdk.Tags.of(app).add(key, value);
  });

  // // Create and configure stacks
  // const stackFactory = new StackFactory(app, stageConfig);
  // const stackConfigs = getStackConfigs(environment, stageConfig.isEphemeral());
  
  // const stacks = stackConfigs
  //   .filter(config => config.enabled)
  //   .map(config => stackFactory.createStack(config))
  //   .filter((stack): stack is cdk.Stack => stack !== null);
  // Create RedirectApiStack
  new RedirectApiStack(app, stageConfig.getResourceName('redirect-api'), {
    lambdaConfig: {
      runtime: lambda.Runtime.PYTHON_3_12,
      memorySize: 1024,
      timeout: 30,
    },
    apiConfig: {
      loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
    },
  }, stageConfig);

  // Apply aspects
  await applyGlobalAspects(app, stageConfig);

  app.synth();
}

async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
  const iamPath = await getParameterValue(`/account_vars/iam/path`);

  // Apply IAM aspects using stageConfig's permission boundary
  cdk.Aspects.of(app).add(new IamPathAspect(iamPath));
  cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(stageConfig.permissionsBoundaryArn));
  cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));

  if (process.env.CDK_DEBUG) {
    console.log('Applied Global Aspects:', {
      environment: stageConfig.environment,
      iamPath,
      permissionsBoundary: stageConfig.permissionsBoundaryArn,
      isEphemeral: stageConfig.isEphemeral(),
    });
  }
}

main().catch(error => {
  console.error('Error initializing CDK app:', error);
  process.exit(1);
});

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
// import { StackFactory } from '../lib/factories/stack-factory';
// import { getStackConfigs } from '../config/stack-definition';
// async function main() {
//   // const environment = process.env.DEPLOY_ENV || 'dev';
//   const environment = app.node.tryGetContext('environment') || 
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

//   // Initialize CDK App with synthesizer configuration
//   const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
//   const synthesizerConfig = JSON.parse(synthesizerConfigJson);

//   // Debug logging for synthesizer config
//   if (process.env.CDK_DEBUG) {
//     console.log('Synthesizer Config:', {
//       permissionsBoundary: synthesizerConfig.iamPermissionsBoundary,
//       environment,
//       ephemeralId,
//     });
//   }

//   const app = new cdk.App({
//     defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(synthesizerConfig),
//   });

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

  // // Create and configure stacks
  // const stackFactory = new StackFactory(app, stageConfig);
  // const stackConfigs = getStackConfigs(environment, stageConfig.isEphemeral());
  
  // const stacks = stackConfigs
  //   .filter(config => config.enabled)
  //   .map(config => stackFactory.createStack(config))
  //   .filter((stack): stack is cdk.Stack => stack !== null);
  // Create RedirectApiStack
//   new RedirectApiStack(app, stageConfig.getResourceName('redirect-api'), {
//     lambdaConfig: {
//       runtime: lambda.Runtime.PYTHON_3_12,
//       memorySize: 1024,
//       timeout: 30,
//     },
//     apiConfig: {
//       loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
//     },
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

// async function main() {
//   const environment = process.env.DEPLOY_ENV || 'dev';
//   const prNumber = process.env.GITHUB_EVENT_NUMBER || '';
//   const ephemeralId = prNumber ? `eph-${prNumber}` : undefined;

//   const context = validateEnvironmentContext(
//     environment,
//     ephemeralId,
//     process.env.GITHUB_REF,
//     prNumber
//   );

//   // Initialize CDK App with synthesizer configuration
//   const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
//   const synthesizerConfig = JSON.parse(synthesizerConfigJson);

//   const app = new cdk.App({
//     defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(synthesizerConfig),
//   });

//   // Create StageConfig
//   const stageConfig = await StageConfig.create(context.environment, ephemeralId);

//   // Set global tags
//   const tags = stageConfig.getStackTags();
//   Object.entries(tags).forEach(([key, value]) => {
//     cdk.Tags.of(app).add(key, value);
//   });

//   // Create RedirectApiStack
//   new RedirectApiStack(app, stageConfig.getResourceName('redirect-api'), {
//     lambdaConfig: {
//       runtime: lambda.Runtime.PYTHON_3_9,
//       memorySize: 128,
//       timeout: 30,
//     },
//     // Optional: custom API Gateway config
//     apiConfig: {
//       loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
//     },
//   }, stageConfig);

//   // Apply aspects
//   await applyGlobalAspects(app, stageConfig);

//   app.synth();
// }

// async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
//   const iamPath = await getParameterValue(`/account_vars/iam/path`);
//   const permissionsBoundaryArn = await getParameterValue(
//     `/account_vars/iam/permissions_boundary_policy`
//   );

//   cdk.Aspects.of(app).add(new IamPathAspect(iamPath));
//   cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(permissionsBoundaryArn));
//   cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));

//   if (process.env.CDK_DEBUG) {
//     console.log(`Applied global aspects for environment: ${stageConfig.environment}`);
//     console.log(`IAM Path: ${iamPath}`);
//     console.log(`Is Ephemeral: ${stageConfig.isEphemeral()}`);
//   }
// }

// main().catch(error => {
//   console.error('Error initializing CDK app:', error);
//   process.exit(1);
// });

// #!/usr/bin/env node

// import * as cdk from 'aws-cdk-lib';
// import { getParameterValue } from '../utils/parameter-store';
// import { validateEnvironmentContext } from '../config/environment-config';
// import { RedirectApiStack } from '../lib/stacks/redirect-stack';
// import { StackFactory } from '../lib/factories/stack-factory';
// import { getStackConfigs } from '../config/stack-definition';
// import { StageConfig } from '../config/stage-config';
// import { IamPathAspect } from '../lib/aspects/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
// import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';

// async function main() {
//   const environment = process.env.DEPLOY_ENV || 'dev';
//   const prNumber = process.env.GITHUB_EVENT_NUMBER || '';
//   const ephemeralId = prNumber ? `eph-${prNumber}` : undefined;

//   const context = validateEnvironmentContext(
//     environment, 
//     ephemeralId, 
//     process.env.GITHUB_REF, 
//     prNumber
//   );

//   // Initialize the CDK App with synthesizer configuration
//   const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
//   const synthesizerConfig = JSON.parse(synthesizerConfigJson);

//   const app = new cdk.App({
//     defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(synthesizerConfig),
//   });

//   // Fetch environment-specific configuration using StageConfig
//   const stageConfig = await StageConfig.create(context.environment, ephemeralId);

//   // Set global tags for the app based on StageConfig
//   const tags = stageConfig.getStackTags();
//   Object.entries(tags).forEach(([key, value]) => {
//     cdk.Tags.of(app).add(key, value);
//   });

//   // Initialize StackFactory to create stacks based on configuration
//   const stackFactory = new StackFactory(app, stageConfig);

//   // Deploy stacks as defined in the configurations
//   const stackConfigs = getStackConfigs(context.environment, stageConfig.isEphemeral());
//   const stacks = stackConfigs
//     .filter(config => config.enabled)
//     .map(config => stackFactory.createStack(config))
//     .filter(Boolean); // Ensure no null stacks if any are disabled

//   // Apply all aspects globally to the app
//   await applyGlobalAspects(app, stageConfig);

//   // Synthesize the app for deployment
//   app.synth();
// }

// /**
//  * Applies all global aspects to the CDK app
//  * @param app - The CDK app instance
//  * @param stageConfig - The stage configuration
//  */
// async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
//   // Apply IAM aspects
//   const iamPath = await getParameterValue(`/account_vars/iam/path`);
//   const permissionsBoundaryArn = await getParameterValue(
//     `/account_vars/iam/permissions_boundary_policy`
//   );

//   // Apply IAM aspects
//   cdk.Aspects.of(app).add(new IamPathAspect(iamPath));
//   cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(permissionsBoundaryArn));

//   // Apply removal policy aspect using StageConfig
//   cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));

//   // Log aspects application if in debug mode
//   if (process.env.CDK_DEBUG) {
//     console.log(`Applied global aspects for environment: ${stageConfig.environment}`);
//     console.log(`IAM Path: ${iamPath}`);
//     console.log(`Is Ephemeral: ${stageConfig.isEphemeral()}`);
//   }
// }

// // Execute main function and handle any errors during the process
// main().catch(error => {
//   console.error('Error initializing CDK app:', error);
//   process.exit(1);
=======
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
//import { RedirectStack } from '../lib/stacks/redirect-stack';
import { EnvironmentConfig } from '../config/environment-config';
//import { StaticAssetsStack } from '../lib/stacks/static-asset-construct';
import { HelloWorldStack } from '../lib/stacks/hello-world-stack';

async function main() {
  const branchName = process.env.GITHUB_REF_NAME || 'main';
  const prNumber = process.env.GITHUB_EVENT_NUMBER;
  const account = process.env.AWS_ACCOUNT_ID;
  const region = process.env.AWS_DEFAULT_REGION;
  const stage = process.env.STAGE;

  const config = new EnvironmentConfig(branchName, account, prNumber);

  const customSynthesizer = new cdk.DefaultStackSynthesizer({
    qualifier: 'one',
    cloudFormationExecutionRole:
      `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-cfn-exec-role-${account}-${region}`,
    deployRoleArn:
      `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-deploy-role-${account}-${region}`,
    fileAssetPublishingRoleArn:
      `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-file-publishing-role-${account}-${region}`,
    imageAssetPublishingRoleArn:
      `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-image-publishing-role-${account}-${region}`,
    lookupRoleArn:
      `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-lookup-role-${account}-${region}`,
  });

  const app = new cdk.App({
    defaultStackSynthesizer: customSynthesizer,
  });

  // Apply Aspects (like IAM path and permissions boundary) to the entire app
  config.applyAspects(app);

  // Create stacks based on the configuration
  new HelloWorldStack(app, `${stage}-HelloWorldStack`, {
    env: {
      account: account,
      region: region,
    },
  });
  // new RedirectStack(app, `${config.stackPrefix}-RedirectStack`, {
  //   env: {
  //     account: config.accountId,
  //     region: config.region,
  //   },
  // });
  // new StaticAssetsStack(app, `${config.stackPrefix}-StaticAssets`, {
  //   env: { account: config.accountId, region: config.region },
  //   config,
  // });
  console.log(config)
  app.synth();
}

main().catch(error => {
  console.error('Error during deployment:', error);
  process.exit(1);
});



// #!/usr/bin/env node
// import 'source-map-support/register';
// import * as cdk from 'aws-cdk-lib';
// import { RedirectStack } from '../lib/stacks/redirect-stack';
// import { IamPathAspect } from '../lib/constructs/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/constructs/iam-permissions-boundary-aspect';
// import { EnvironmentConfig } from '../config/environment-config';

// // Use environment variables or default to local testing values
// const branchName = process.env.GITHUB_REF_NAME || 'dev';  // Defaults to 'dev' if no env variable is set
// const prNumber = process.env.GITHUB_EVENT_NUMBER || '111'; // Default PR number for local testing

// // Create custom synthesizer for roles and asset management
// const customSynthesizer = new cdk.DefaultStackSynthesizer({
//   qualifier: 'one',
//   cloudFormationExecutionRole: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-cfn-exec-role-${account}-${region}',
//   deployRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-deploy-role-${account}-${region}',
//   fileAssetPublishingRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-file-publishing-role-${account}-${region}',
//   imageAssetPublishingRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-image-publishing-role-${account}-${region}',
//   lookupRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-lookup-role-${account}-${region}',
// });

// // Initialize the CDK App
// const app = new cdk.App({ defaultStackSynthesizer: customSynthesizer });

// // Set up IAM aspects for permissions boundary and path
// cdk.Aspects.of(app).add(
//   new IamPermissionsBoundaryAspect('arn:aws:iam::${account}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy')
// );
// cdk.Aspects.of(app).add(new IamPathAspect('/delegatedadmin/developer/'));

// // Create the environment configuration based on the current branch
// const config = new EnvironmentConfig(branchName, prNumber);

// // Instantiate the Redirect Stack
// new RedirectStack(app, `RedirectStack-${config.stackPrefix}`, {
//   env: {
//     account: config.accountId,
//     region: config.region,
//   },
// });

// // Synthesize the app
// app.synth();



// #!/usr/bin/env node
// import 'source-map-support/register';
// import * as cdk from 'aws-cdk-lib';
// import { RedirectStack } from '../lib/stacks/redirect-stack';
// import { IamPathAspect } from '../lib/constructs/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/constructs/iam-permissions-boundary-aspect';
// import { EnvironmentConfig } from '../config/environment-config';

// // Initialize stage from context or default to 'dev'
// const stage = process.env.STAGE || 'dev';

// // Create custom synthesizer for roles and asset management
// const customSynthesizer = new cdk.DefaultStackSynthesizer({
//   qualifier: 'one',
//   cloudFormationExecutionRole: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-cfn-exec-role-${account}-${region}',
//   deployRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-deploy-role-${account}-${region}',
//   fileAssetPublishingRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-file-publishing-role-${account}-${region}',
//   imageAssetPublishingRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-image-publishing-role-${account}-${region}',
//   lookupRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-lookup-role-${account}-${region}',
// });

// // Initialize the CDK App
// const app = new cdk.App({ defaultStackSynthesizer: customSynthesizer });

// // Set up IAM aspects for permissions boundary and path
// cdk.Aspects.of(app).add(
//   new IamPermissionsBoundaryAspect('arn:aws:iam::${account}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy')
// );
// cdk.Aspects.of(app).add(new IamPathAspect('/delegatedadmin/developer/'));

// // Fetch environment configuration
// const config = new EnvironmentConfig(stage);

// // Instantiate the RedirectStack
// new RedirectStack(app, `RedirectStack-${config.stackPrefix}`, {
//   env: {
//     account: config.accountId,
//     region: config.region,
//   },
// });

// // Synthesize the app
// app.synth();



// #!/usr/bin/env node
// import 'source-map-support/register';
// import * as cdk from 'aws-cdk-lib';
// import { RedirectStack } from '../lib/stacks/redirect-stack';
// import { IamPathAspect } from '../lib/constructs/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/constructs/iam-permissions-boundary-aspect';
// import { EnvironmentConfig } from '../config/environment-config';
// //const app = new cdk.App();
// //const stage = app.node.tryGetContext('stage') || 'dev';
// const customSynthesizer = new cdk.DefaultStackSynthesizer({
//   qualifier: 'one',
//   cloudFormationExecutionRole: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-cfn-exec-role-${account}-${region}',
//   deployRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-deploy-role-${account}-${region}',
//   fileAssetPublishingRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-file-publishing-role-${account}-${region}',
//   imageAssetPublishingRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-image-publishing-role-${account}-${region}',
//   lookupRoleArn: 'arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-lookup-role-${account}-${region}',
// });
// const app = new cdk.App({defaultStackSynthesizer: customSynthesizer});
// //he permissions boundary aspect
// cdk.Aspects.of(app).add(
//   new IamPermissionsBoundaryAspect('arn:aws:iam::${account}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy')
// );
// cdk.Aspects.of(app).add(new IamPathAspect('/delegatedadmin/developer/'));
// app.synth();

// new RedirectStack(app, `RedirectStack-${stage}`, {
//   env: { 
//     account: process.env.CDK_DEFAULT_ACCOUNT, 
//     region: process.env.CDK_DEFAULT_REGION 
//   },
>>>>>>> main
// });

