// src/stacks/base-stack.ts
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { IConstruct } from "constructs";
// import { BaseStackConfig, StackUtils } from '../../config/types/config-types';
// import { ParameterStore } from '../../config/types/parameter-types';
// import { SynthesizerManager } from '../../config/sythesizer-manager';

/**
 * Base stack class with common functionality
 * Extend this for application-specific stacks
 */
// types.ts
interface BaseStackConfig {
    stage: string;
    prNumber?: string;
    isExperimental: boolean;
   }
   
   // base-stack.ts
   abstract class BaseStack extends cdk.Stack {
    constructor(scope: Construct, id: string, config: BaseStackConfig) {
      super(scope, id, {
        tags: {
          Environment: config.stage,
          PRNumber: config.prNumber || 'N/A' 
        }
      });
   
      // Apply removal policy to all resources in the stack
      if (config.isExperimental) {
        cdk.Aspects.of(this).add({
          visit(node: IConstruct) {
            if (node instanceof cdk.Resource) {
              node.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
            }
          }
        });
      }
    }
   
    protected abstract createResources(): void;
   }