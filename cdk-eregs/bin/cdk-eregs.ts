// bin/main-app.ts
import * as cdk from 'aws-cdk-lib';
import { RedirectStack } from '../lib/stacks/redirect-stack';
import { StaticAssetsStack } from '../lib/stacks/static-asset-construct';
//import { MaintenanceLambdaStack } from '../lib/stacks/maintenance-lamba-stack';
import { EcfrStack } from '../lib/stacks/ecfr-stack';
import { FrStack } from '../lib/stacks/fr-stack';
import { EnvironmentConfigStack } from '../config/environment-config';
import { Environment } from '../config/types/config-types';

class MainApp {
  private readonly app: cdk.App;
  private readonly environment: Environment;
  private readonly envConfigStack: EnvironmentConfigStack;

  constructor() {
    // Initialize CDK app with custom synthesizer
    this.app = new cdk.App({
      defaultStackSynthesizer: this.createSynthesizer(),
    });

    // Determine environment
    this.environment = this.determineEnvironment();

    // Create environment configuration stack
    this.envConfigStack = this.createEnvironmentStack();

    // Deploy application stacks
    this.deployStacks();
  }

  private createSynthesizer(): cdk.DefaultStackSynthesizer {
    const accountId = '009160033411';
    const basePath = 'delegatedadmin/developer';
    
    return new cdk.DefaultStackSynthesizer({
      qualifier: 'one',
      cloudFormationExecutionRole: `arn:aws:iam::${accountId}:role/${basePath}/cdk-one-cfn-exec-role-${accountId}-us-east-1`,
      deployRoleArn: `arn:aws:iam::${accountId}:role/${basePath}/cdk-one-deploy-role-${accountId}-us-east-1`,
      fileAssetPublishingRoleArn: `arn:aws:iam::${accountId}:role/${basePath}/cdk-one-file-publishing-role-${accountId}-us-east-1`,
      imageAssetPublishingRoleArn: `arn:aws:iam::${accountId}:role/${basePath}/cdk-one-image-publishing-role-${accountId}-us-east-1`,
      lookupRoleArn: `arn:aws:iam::${accountId}:role/${basePath}/cdk-one-lookup-role-${accountId}-us-east-1`,
    });
  }

  private determineEnvironment(): Environment {
    const gitBranch = process.env.GIT_BRANCH || 'dev';
    
    switch (gitBranch) {
      case 'main':
        return 'dev';
      case 'val':
        return 'val';
      case 'production':
        return 'prod';
      default:
        return 'experimental';
    }
  }

  private createEnvironmentStack(): EnvironmentConfigStack {
    return new EnvironmentConfigStack(this.app, `EnvironmentConfigStack-${this.environment}`, {
      env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
      }
    });
  }

  private deployStacks(): void {
    const { baseConfig } = this.envConfigStack;
    const defaultEnv = {
      account: baseConfig.accountId,
      region: baseConfig.region
    };

    // Deploy RedirectStack
    new RedirectStack(this.app, `${baseConfig.stackPrefix}-RedirectStack`, {
      env: defaultEnv,
      envStack: this.envConfigStack
    });

    // Deploy StaticAssetsStack
    // new StaticAssetsStack(this.app, `${baseConfig.stackPrefix}-StaticAssets`, {
    //   env: defaultEnv,
    //   envStack: this.envConfigStack
    // });

    // Deploy MaintenanceLambdaStack
    // new MaintenanceLambdaStack(this.app, `${baseConfig.stackPrefix}-MaintenanceLambda`, {
    //   env: defaultEnv,
    //   envStack: this.envConfigStack
    // });

    // Deploy Parser Stacks
    new EcfrStack(this.app, `${baseConfig.stackPrefix}-Ecfr`, {
      env: defaultEnv,
      envStack: this.envConfigStack
    });

    new FrStack(this.app, `${baseConfig.stackPrefix}-Fr`, {
      env: defaultEnv,
      envStack: this.envConfigStack
    });

    // Add stack dependencies
    this.addStackDependencies();
  }

  private addStackDependencies(): void {
    // Add any necessary stack dependencies here
  }

  public synth(): void {
    this.app.synth();
  }
}

// Execute the deployment
try {
  const app = new MainApp();
  app.synth();
} catch (error) {
  console.error('Error during deployment:', error);
  process.exit(1);
}