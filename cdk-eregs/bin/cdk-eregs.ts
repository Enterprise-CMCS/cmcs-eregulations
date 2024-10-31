#!/usr/bin/env node
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

  const config = new EnvironmentConfig(branchName, prNumber);

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
// });

