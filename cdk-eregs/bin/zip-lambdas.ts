#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { getParameterValue } from '../utils/parameter-store';
import { validateEnvironmentContext } from '../config/environment-config';
import { RedirectApiStack } from '../lib/stacks/redirect-stack';
import { StageConfig } from '../config/stage-config';
import { IamPathAspect } from '../lib/aspects/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { MaintenanceApiStack } from '../lib/stacks/maintainance-stack';
import { S3ImportStack } from '../lib/stacks/s3-import';
import { StaticAssetsStack } from '../lib/stacks/static-assets-stack';
import { APIStack } from '../lib/stacks/api-stack';

async function main() {
    const synthesizerConfigJson = await getParameterValue('/eregulations/cdk_config');
    const synthesizerConfig = JSON.parse(synthesizerConfigJson);

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

    const tags = stageConfig.getStackTags();
    Object.entries(tags).forEach(([key, value]) => {
      cdk.Tags.of(app).add(key, value);
    });
     
    // Fetch required infrastructure parameters
    const [
      vpcId,
      privateSubnetAId,
      privateSubnetBId,
      iamPath
    ] = await Promise.all([
      getParameterValue('/account_vars/vpc/id'),
      getParameterValue('/account_vars/vpc/subnets/private/1b/id'),
      getParameterValue('/account_vars/vpc/subnets/private/b/id'),
      getParameterValue('/account_vars/iam/path'),
    ]);

    // Create API stack
    const apiStack = new APIStack(app, stageConfig.getResourceName('api'), {
      env: {
        account: process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID,
        region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
      },
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

    // Create ZIP-based Lambda stacks
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

    new MaintenanceApiStack(app, stageConfig.getResourceName('maintenance-api'), {
      lambdaConfig: {
        runtime: lambda.Runtime.PYTHON_3_12,
        memorySize: 1024,
        timeout: 30,
      },
      apiConfig: {
        loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
      },
    }, stageConfig);
     // 8. Retrieve the Certificate ARN from SSM (or wherever it is stored)
  const certificateArn = await getParameterValue('/eregulations/acm-cert-arn');

  // 9. Create the StaticAssetsStack with the certificateArn
  new StaticAssetsStack(
    app,
    stageConfig.getResourceName('static-assets'),  // the "id"
    {
      env,
      description: `Static Assets Stack for ${stageConfig.getResourceName('site')}`,
      certificateArn, // put certificateArn in props if you like
    },
    stageConfig // 4th param, passed separately
  );

   
  //Create static assets stack

 // Create static assets stack and initialize resources
//  const staticAssetsStack = new StaticAssetsStack(app, stageConfig.getResourceName('static-assets'), {
//   env,
//   description: `Static Assets Stack for ${stageConfig.getResourceName('site')}`,
// }, stageConfig);
// // Explicit, forceful logging
// console.error('Stack Creation Explicit Debug:', {
//   stackName: stageConfig.getResourceName('static-assets'),
//   env: JSON.stringify(env),
//   siteAssetsName: stageConfig.getResourceName('site-assets'),
//   stackConfig: {
//     environment: stageConfig.environment,
//     ephemeralId: stageConfig.ephemeralId,
//     isEphemeral: stageConfig.isEphemeral()
//   }
// });
  // Create the SimpleBucketStack
 // Create the SimpleBucketStack
 console.log('Creating SimpleBucketStack');
    

// Call create() to initialize the stack's resources

    // Debug output for configuration
    console.log('Configuration Debug:', {
      environment: context.environment,
      ephemeralId,
      prNumber,
      isEphemeral: stageConfig.isEphemeral(),
      resourceExample: stageConfig.getResourceName('site-assets')
    });
    console.log('Configuration Debug:', {
      determinedEnvironment: context.environment,
      prNumber,
      ephemeralId,
      deployEnv: process.env.DEPLOY_ENV,
      githubJobEnv: process.env.GITHUB_JOB_ENVIRONMENT
    });
    new S3ImportStack(app, 'S3ImportStack', {
      bucketName: process.env.BUCKET_NAME || '',
      env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION,
      },
    });

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