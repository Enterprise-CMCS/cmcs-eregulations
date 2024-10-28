// src/stacks/base-stack.ts
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { BaseStackConfig ,  StackUtils } from '../../config/types/config-types';
import { ParameterStore } from '../../config/types/parameter-types';
// import { StackUtils } from '../utils/stack-utils';

/**
 * Base stack class with common functionality
 * Extend this for application-specific stacks
 */
export abstract class BaseStack extends cdk.Stack {
  protected readonly parameterStore: ParameterStore;
  protected readonly stackPrefix: string;
  protected readonly removalPolicy: cdk.RemovalPolicy;

  constructor(
    scope: Construct,
    id: string,
    protected readonly config: BaseStackConfig,
    props?: cdk.StackProps
  ) {
    super(scope, id, {
      ...props,
      tags: StackUtils.getCommonTags(config),
    });

    this.parameterStore = ParameterStore.getInstance(this, config.stage);
    this.stackPrefix = StackUtils.getStackPrefix(config.stage, config.prNumber);
    this.removalPolicy = StackUtils.getRemovalPolicy(config.isExperimental);
  }

  /**
   * Method to be implemented by derived stacks for resource creation
   */
  protected abstract createResources(): void;

  /**
   * Gets a resource name with proper prefix
   */
  protected getResourceName(resourceType: string, name: string): string {
    return `${this.stackPrefix}-${name}-${resourceType}`;
  }
}
