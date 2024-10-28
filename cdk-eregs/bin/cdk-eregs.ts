#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { RedirectStack } from '../lib/stacks/redirect-stack';
import { Environment, EnvironmentConfig, StackUtils } from '../config/types/config-types';
import { ENVIRONMENT_CONFIGS } from '../config/environment-config';
import { SynthesizerManager } from '../config/sythesizer-manager';


class App {
  private readonly app: cdk.App;
  private readonly stage: Environment;
  private readonly prNumber?: string;

  constructor() {
    // Get deployment configuration
    this.stage = this.getStage();
    this.prNumber = process.env.PR_NUMBER;

    // Validate deployment
    this.validateDeployment();

    // Initialize app with custom synthesizer
    this.app = this.createApp();

    // Create stacks
    this.createStacks();
  }

  private getStage(): Environment {
    const stage = (
      process.env.STAGE || 
      process.env.CDK_DEFAULT_STAGE || 
      'dev'
    ) as Environment;

    if (!['dev', 'val', 'prod'].includes(stage)) {
      throw new Error(`Invalid stage: ${stage}`);
    }

    return stage;
  }

  private validateDeployment(): void {
    if (this.prNumber && this.stage !== 'dev') {
      throw new Error('Experimental deployments are only allowed in dev stage');
    }
  }

  private createApp(): cdk.App {
    const tempApp = new cdk.App();
    const synthesizerManager = new SynthesizerManager(tempApp);
    const synthesizer = synthesizerManager.getSynthesizer(this.stage);

    return new cdk.App({
      defaultStackSynthesizer: synthesizer
    });
  }

  private createStacks(): void {
    const envConfig = ENVIRONMENT_CONFIGS[this.stage];
    const isExperimental = StackUtils.isExperimentalDeployment(this.prNumber);
    const stackPrefix = StackUtils.getStackPrefix(this.stage, this.prNumber);

    new RedirectStack(this.app, `${stackPrefix}-redirect-stack`, {
      stage: this.stage,
      prNumber: this.prNumber,
      env: {
        account: envConfig.account,
        region: envConfig.region,
      },
      description: `Redirect API Stack - ${this.stage.toUpperCase()}${
        isExperimental ? ` (PR #${this.prNumber})` : ''
      }`,
    });
  }

  public synth(): void {
    this.app.synth();
  }
}


