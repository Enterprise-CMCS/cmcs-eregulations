// config-manager.ts
import { DeploymentConfig, Environment } from '../config/types/config-types';
import { getParameterValue } from './parameter-store';

export class ConfigManager {
  /**
   * Validates environment variables and returns deployment config
   */
  static async getConfig(): Promise<DeploymentConfig> {
    // Validate required env vars
    const project = this.validateEnvVar('PROJECT');
    const stage = this.validateEnvVar('STAGE') as Environment;
    const prNumber = process.env.PR_NUMBER;

    // Validate stage value
    if (!['dev', 'val', 'prod'].includes(stage)) {
      throw new Error(`Invalid stage: ${stage}. Must be one of: dev, val, prod`);
    }

    // Validate PR deployments only in dev
    if (prNumber && stage !== 'dev') {
      throw new Error('PR deployments are only allowed in dev environment');
    }

    try {
      // Fetch configs from SSM
      const [synthConfig, iamConfig] = await Promise.all([
        getParameterValue('/cms/cloud/cdkSynthesizerConfig'),
        getParameterValue('/cms/cloud/iamConfig')
      ]);

      return {
        project,
        stage,
        prNumber,
        isExperimental: Boolean(prNumber),
        ...JSON.parse(iamConfig),
        synthesizerConfig: JSON.parse(synthConfig)
      };
    } catch (error) {
      throw new Error(`Failed to load configuration: ${error.message}`);
    }
  }

  /**
   * Validates existence of required environment variables
   * @param name Environment variable name
   * @returns Environment variable value
   * @throws Error if environment variable is not set
   */
  private static validateEnvVar(name: string): string {
    const value = process.env[name];
    if (!value) {
      throw new Error(`Required environment variable ${name} is not set`);
    }
    return value;
  }
}