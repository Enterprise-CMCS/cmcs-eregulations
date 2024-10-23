// app.ts
import * as cdk from 'aws-cdk-lib';
import { ConfigManager } from '../config/environment-config';
// import { ApiStack } from './stacks/api-stack';
import { }

async function main() {
  try {
    // Get validated config with all required env vars
    const config = await ConfigManager.getConfig();

    const app = new cdk.App({
      defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(
        config.synthesizerConfig
      )
    });

    // Create stacks with validated config
    new ApiStack(app, `${config.project}-api-${config.stage}`, {
      config,
      env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION
      },
      apiName: 'users',
      allowedOrigins: ['*']
    });

    app.synth();
  } catch (error) {
    console.error('Deployment failed:', error);
    process.exit(1);
  }
}

main();