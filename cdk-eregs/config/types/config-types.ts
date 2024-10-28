// src/types/config-types.ts\
import * as cdk from 'aws-cdk-lib';
export type Environment = 'dev' | 'val' | 'prod';

export interface EnvironmentConfig {
  account: string;
  region: string;
}

/**
 * Base configuration for all stacks
 */
export interface BaseStackConfig {
  /** Stack name */
  name: string;
  /** Deployment stage */
  stage: Environment;
  /** PR number for experimental deployments */
  prNumber?: string;
  /** Whether this is an experimental deployment */
  isExperimental: boolean;
}

// src/utils/stack-utils.ts

export class StackUtils {
  /**
   * Determines if a deployment is experimental based on PR number
   */
  static isExperimentalDeployment(prNumber?: string): boolean {
    return !!prNumber;
  }

  /**
   * Gets stack prefix based on deployment type
   */
  static getStackPrefix(stage: Environment, prNumber?: string): string {
    return prNumber ? `pr-${prNumber}` : stage;
  }

  /**
   * Gets stack removal policy based on deployment type
   */
  static getRemovalPolicy(isExperimental: boolean): cdk.RemovalPolicy {
    return isExperimental ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN;
  }

  /**
   * Gets common tags for all resources
   */
  static getCommonTags(config: BaseStackConfig): { [key: string]: string } {
    return {
      Environment: config.stage,
      Service: config.name,
      ManagedBy: 'CDK',
      ...(config.isExperimental && {
        PR: config.prNumber!,
        Temporary: 'true',
        ExperimentalDeployment: 'true',
      }),
    };
  }
}