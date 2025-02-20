#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { getParameterValue } from '../utils/parameter-store';
import { validateEnvironmentContext } from '../config/environment-config';
import { StageConfig } from '../config/stage-config';
import { IamPathAspect } from '../lib/aspects/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
import { TextExtractorStack } from '../lib/stacks/text-extract-stack';
import { FrParserStack } from '../lib/stacks/fr-parser-stack';
import { EcfrParserStack } from '../lib/stacks/ecfr-parser-stack';
import { BackendStack } from '../lib/stacks/api-stack';

async function main() {
    const synthesizerConfigJson = await getParameterValue('/eregulations/cdk_config');
    const synthesizerConfig = JSON.parse(synthesizerConfigJson);

    const [

      logLevel,
      httpUser,
      httpPassword,
      eregsApiUrl
    ] = await Promise.all([

      getParameterValue('/eregulations/text_extractor/log_level'),
      getParameterValue('/eregulations/http/user'),
      getParameterValue('/eregulations/http/password'),
      getParameterValue('/eregulations/custom_url'),
    ]);
   // Fetch required infrastructure parameters
   const [
    vpcId,
    privateSubnetAId,
    privateSubnetBId,
    iamPath
  ] = await Promise.all([
    getParameterValue('/account_vars/vpc/id'),
    getParameterValue('/account_vars/vpc/subnets/private/1a/id'),
    getParameterValue('/account_vars/vpc/subnets/private/1b/id'),
    getParameterValue('/account_vars/iam/path'),
  ]);


    const env = {
      account: process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID,
      region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
    };

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

    if (process.env.CDK_DEBUG) {
      console.log('Synthesizer Config:', {
        permissionsBoundary: synthesizerConfig.iamPermissionsBoundary,
        environment,
        ephemeralId,
      });
    }

    const stageConfig = await StageConfig.create(
      context.environment,
      ephemeralId,
      synthesizerConfig.iamPermissionsBoundary
    );

    if (process.env.CDK_DEBUG) {
      console.log('StageConfig Details:', {
        environment: stageConfig.environment,
        permissionsBoundary: stageConfig.permissionsBoundaryArn,
        isEphemeral: stageConfig.isEphemeral(),
        ephemeralId: ephemeralId,
      });
    }

    // // Create Docker-based Lambda stacks
    // new TextExtractorStack(app, stageConfig.getResourceName('text-extractor'), {
    //   env,
    //   lambdaConfig: {
    //     memorySize: 1024,
    //     timeout: 900,
    //     reservedConcurrentExecutions: 10,
    //   },
    //   environmentConfig: {
    //     vpcId,
    //     logLevel,
    //     httpUser,
    //     httpPassword,
    //   }
    // }, stageConfig);
    new TextExtractorStack(app, stageConfig.getResourceName('text-extractor'), {
      env,
      lambdaConfig: {
        memorySize: 1024,
        timeout: 900,
      },
      environmentConfig: {
        logLevel,
        httpUser,
        httpPassword,
      }
    }, stageConfig);
    new FrParserStack(app, stageConfig.getResourceName('fr-parser'), {
      env,
      lambdaConfig: {
        timeout: 900,
      },
      environmentConfig: {
        logLevel,
        httpUser,
        httpPassword,
      }
    }, stageConfig);

    new EcfrParserStack(app, stageConfig.getResourceName('ecfr-parser'), {
      env,
      lambdaConfig: {
        timeout: 900,
      },
      environmentConfig: {
        logLevel,
        httpUser,
        httpPassword,
      }
    }, stageConfig);
        // Create API stack with Docker-based Lambdas
        const apiStack = new BackendStack(app, stageConfig.getResourceName('api'), {
          env,
          description: `API Stack for ${stageConfig.getResourceName('site')}`,
          lambdaConfig: {
            memorySize: 4096,
            timeout: 30,
          },
          environmentConfig: {
            vpcId,
            logLevel: process.env.LOG_LEVEL || 'INFO',
            subnetIds: [privateSubnetAId, privateSubnetBId],
          }
        }, stageConfig);


    await applyGlobalAspects(app, stageConfig);

    app.synth();
}

async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
  const iamPath = await getParameterValue(`/account_vars/iam/path`);

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
