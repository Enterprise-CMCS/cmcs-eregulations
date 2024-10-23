import * as cdk from 'aws-cdk-lib';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { Environment } from './types/config-types';
import { ParameterStore } from './types/parameter-types';

interface SynthesizerConfig {
    qualifier: string;
    cloudFormationExecutionRole: string;
    deployRoleArn: string;
    fileAssetPublishingRoleArn: string;
    imageAssetPublishingRoleArn: string;
    lookupRoleArn: string;
  }
  
  export class SynthesizerManager {
    constructor(private readonly scope: Construct) {}
  
    public getSynthesizer(stage: Environment): cdk.DefaultStackSynthesizer {
      try {
        // Use existing ParameterStore
        const parameterStore = ParameterStore.getInstance(this.scope, stage);
        
        // Get synthesizer config using the parameter store
        const config = parameterStore.getParameter<SynthesizerConfig>('SYNTHESIZER', 'CONFIG');
        
        // Create synthesizer with the config
        return new cdk.DefaultStackSynthesizer({
          qualifier: config.qualifier,
          cloudFormationExecutionRole: config.cloudFormationExecutionRole,
          deployRoleArn: config.deployRoleArn,
          fileAssetPublishingRoleArn: config.fileAssetPublishingRoleArn,
          imageAssetPublishingRoleArn: config.imageAssetPublishingRoleArn,
          lookupRoleArn: config.lookupRoleArn,
        });
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        throw new Error(`Failed to load synthesizer configuration for stage ${stage}: ${errorMessage}`);
      }
    }
  }
// export class SynthesizerManager {
//   constructor(private readonly scope: Construct) {}

//   public getSynthesizer(stage: Environment): cdk.DefaultStackSynthesizer {
//     try {
//       const synthesizerJson = ssm.StringParameter.valueForStringParameter(
//         this.scope,
//         `/cms/cloud/cdkSynthesizerConfig`
//       );
      
//       const roles = JSON.parse(synthesizerJson);
//       return new cdk.DefaultStackSynthesizer({
//         qualifier: roles.qualifier,
//         cloudFormationExecutionRole: roles.cloudFormationExecutionRole,
//         deployRoleArn: roles.deployRoleArn,
//         fileAssetPublishingRoleArn: roles.fileAssetPublishingRoleArn,
//         imageAssetPublishingRoleArn: roles.imageAssetPublishingRoleArn,
//         lookupRoleArn: roles.lookupRoleArn,
//       });
//     }
//       catch (error: unknown) {
//         const errorMessage = error instanceof Error ? error.message : String(error);
//         throw new Error(`Failed to load synthesizer configuration for stage ${stage}: ${errorMessage}`);
//       }

//   }
// }
