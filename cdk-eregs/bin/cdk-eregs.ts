#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { VpcStack } from '../lib/stacks/vpc-stack';
import { BackendStack } from '../lib/stacks/api-stack';
import { StaticAssetsStack } from '../lib/stacks/static-assets-stack';
import { EcfrParserStack } from '../lib/stacks/ecfr-parser-stack';
import { FrParserStack } from '../lib/stacks/fr-parser-stack';
import { TextExtractorStack } from '../lib/stacks/text-extract-stack';
import { StageConfig } from '../config/stage-config';
import { getParameterValue } from '../utils/parameter-store';

const app = new cdk.App();
const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
};

async function main() {
  // Create StageConfig for prod
  const stageConfig = await StageConfig.create(
    'prod',
    undefined,
    'arn:aws:iam::aws:policy/PowerUserAccess'
  );

  // Get infrastructure parameters
  const [vpcId, subnet1a, subnet1b, httpUser, httpPassword] = await Promise.all([
    getParameterValue('/account_vars/vpc/prod/id'),
    getParameterValue('/account_vars/vpc/prod/subnets/private/1a/id'),
    getParameterValue('/account_vars/vpc/prod/subnets/private/1b/id'),
    getParameterValue('/eregulations/http/user'),
    getParameterValue('/eregulations/http/password'),
  ]);

  // Only create the VPC stack if we're deploying it
  const stackName = process.argv[3];
  if (!stackName || stackName === 'a1m-eregs-prod-vpc') {
    new VpcStack(app, 'a1m-eregs-prod-vpc', { env });
  }

  if (!stackName || stackName === 'a1m-eregs-prod-static') {
    // Get deployment type from context or default to 'content'
    const deploymentType = app.node.tryGetContext('deploymentType') || 'content';

    new StaticAssetsStack(app, 'a1m-eregs-prod-static', {
      env,
      deploymentType,
      certificateArn: process.env.CERTIFICATE_ARN,
    }, stageConfig);
  }

  // Only create the API stack if we're deploying it
  if (!stackName || stackName === 'a1m-eregs-prod-api') {
    new BackendStack(app, 'a1m-eregs-prod-api', {
      env,
      environmentConfig: {
        vpcId,
        logLevel: 'INFO',
        subnetIds: [subnet1a, subnet1b]
      },
      lambdaConfig: {
        memorySize: 1024,
        timeout: 30
      }
    }, stageConfig);
  }

  // Add parser stacks
  if (!stackName || stackName.includes('fr-parser') || stackName.includes('ecfr-parser')) {
    // Create eCFR Parser Stack
    new EcfrParserStack(app, 'a1m-eregs-prod-ecfr-parser', {
      env,
      environmentConfig: {
        httpUser,
        httpPassword,
        logLevel: 'INFO'
      },
      lambdaConfig: {
        timeout: 900  // 15 minutes
      }
    }, stageConfig);

    // Create FR Parser Stack
    new FrParserStack(app, 'a1m-eregs-prod-fr-parser', {
      env,
      environmentConfig: {
        httpUser,
        httpPassword,
        logLevel: 'INFO'
      },
      lambdaConfig: {
        timeout: 900  // 15 minutes
      }
    }, stageConfig);
  }

  if (!stackName || stackName === 'a1m-eregs-prod-text-extractor') {
    new TextExtractorStack(app, 'a1m-eregs-prod-text-extractor', {
      env,
      environmentConfig: {
        logLevel: 'INFO',
        httpUser,
        httpPassword
      },
      lambdaConfig: {
        memorySize: 1024,
        timeout: 900  // 15 minutes
      }
    }, stageConfig);
  }

  app.synth();
}

main().catch(error => {
  console.error('Error:', error);
  process.exit(1);
});
