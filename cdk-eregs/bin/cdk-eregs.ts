#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
//import { RedirectStack } from '../lib/stacks/redirect-stack';
import { EnvironmentConfig } from '../config/environment-config';
import { StaticAssetsStack } from '../lib/stacks/static-asset-construct';
import { MaintenanceLambdaStack } from '../lib/stacks/maintenance-lamba-stack';
import { EcfrStack } from '../lib/stacks/ecfr-stack';
//import {ssm}
async function main() {
  // const branchName = process.env.GITHUB_REF_NAME || 'main';
  // const prNumber = process.env.GITHUB_EVENT_NUMBER;

  // const config = new EnvironmentConfig(branchName, prNumber);
 
//const app = new cdk.App();

const branchName = process.env.GITHUB_REF_NAME || 'main';
//When creating EnvironmentConfig:
const prNumber = process.env.GITHUB_EVENT_NUMBER || ''; // Defau
//const prNumber = process.env.GITHUB_EVENT_NUMBER;
const customSynthesizer = new cdk.DefaultStackSynthesizer({
  qualifier: 'one',
  cloudFormationExecutionRole:
    'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-cfn-exec-role-009160033411-us-east-1',
  deployRoleArn:
    'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-deploy-role-009160033411-us-east-1',
  fileAssetPublishingRoleArn:
    'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-file-publishing-role-009160033411-us-east-1',
  imageAssetPublishingRoleArn:
    'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-image-publishing-role-009160033411-us-east-1',
  lookupRoleArn:
    'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-lookup-role-009160033411-us-east-1',
});

const app = new cdk.App({
  defaultStackSynthesizer: customSynthesizer,
});

const config = new EnvironmentConfig(app, branchName, prNumber);


  
  // Apply Aspects (like IAM path and permissions boundary) to the entire app
  config.applyAspects(app);

  // Create stacks based on the configuration
  // new RedirectStack(app, `${config.stackPrefix}-RedirectStack`, {
  //   env: {
  //     account: config.accountId,
  //     region: config.region,
  //   },
  // });
  new StaticAssetsStack(app, `${config.stackPrefix}-StaticAssets`, {
    env: { account: config.accountId, region: config.region },
    config,
  });
    // Synthesize stack for Maintenance Lambda
  new MaintenanceLambdaStack(app, `MaintenanceLambdaStack-${config.stackPrefix}`, {
      stage: config.stackPrefix,
      env: {
        account: config.accountId,
        region: config.region,
      },
    });
  // Fetch the VPC ID from SSM Parameter Store
  //const vpcId = ssm.StringParameter.valueForStringParameter(app, `/account_vars/vpc/id`);

  // Look up VPC using the fetched VPC ID
  // const vpc = ec2.Vpc.fromLookup(app, 'Vpc', {
  //   vpcId,
  // });
  const vpc = cdk.aws_ec2.Vpc.fromLookup(app, 'VPC', {
    vpcId: config.vpcId,
  });
  
  new EcfrStack(app, `${config.stackPrefix}-Ecfr`, {
      env: { account: config.accountId, region: config.region },
      config,
      vpc,
    });
  console.log(config)
  app.synth();
}

main().catch((error) => {
  console.error('Error during deployment:', error);
  process.exit(1);
});



