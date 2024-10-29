#!/usr/bin/env node

import 'source-map-support/register';

import * as cdk from 'aws-cdk-lib';

import { HelloWorldStack } from '../lib/hello-world-stack';

const app = new cdk.App();
const account = process.env.AWS_ACCOUNT_ID;
const region = process.env.AWS_DEFAULT_REGION;
const stage = process.env.DEPLOY_STAGE ? process.env.DEPLOY_STAGE : 'undefined';

const customSynthesizer = new cdk.DefaultStackSynthesizer({
  qualifier: 'one',
  fileAssetsBucketName: `cdk-one-assets-${account}-${region}`,
  bucketPrefix: '',
  cloudFormationExecutionRole: `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-cfn-exec-role-${account}-${region}`,
  deployRoleArn: `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-deploy-role-${account}-${region}`,
  fileAssetPublishingRoleArn: `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-file-publishing-role-${account}-${region}`,
  imageAssetPublishingRoleArn: `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-image-publishing-role-${account}-${region}`,
  lookupRoleArn: `arn:aws:iam::${account}:role/delegatedadmin/developer/cdk-one-lookup-role-${account}-${region}`,
});

const stack = new HelloWorldStack(app, 'HelloWorldStack', stage, {
  synthesizer: customSynthesizer,
  env: {
    account: account,
    region: region,
  },
  permissionsBoundary: cdk.PermissionsBoundary.fromArn(cdk.Arn.format({
    partition: 'aws',
    service: 'iam',
    region: region,
    account: account,
    resource: 'policy',
    resourceName: 'cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy',
  })),
});
