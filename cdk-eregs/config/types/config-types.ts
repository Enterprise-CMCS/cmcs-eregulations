// types.ts
import * as cdk from 'aws-cdk-lib';

export type Environment = 'dev' | 'val' | 'prod';

/**
 * Base configuration for all deployments
 */
export interface DeploymentConfig {
  project: string;
  stage: Environment;
  prNumber?: string;
  iamPath: string;
  iamPermissionsBoundary: string;
  isExperimental: boolean;
  synthesizerConfig: any; 
}

/**
 * Base props that all stacks must implement
 */
export interface BaseStackProps extends cdk.StackProps {
  config: DeploymentConfig;
}

/**
 * Stack-specific props extending base props
 */
export interface RedirectStackProps extends BaseStackProps {
  // Additional redirect-specific props
}

export interface MaintenanceStackProps extends BaseStackProps {
  // Additional maintenance-specific props
}
// // src/types/config-types.ts\
// import * as cdk from 'aws-cdk-lib';
// export type Environment = 'dev' | 'val' | 'prod';

// export interface EnvironmentConfig {
//   account: string;
//   region: string;
// }
// export interface ExtendedStackProps extends cdk.StackProps {
//   stage: Environment;
//   prNumber?: string;
//   name: string;
//   isExperimental: boolean;
// }

// /**
//  * Base configuration for all stacks
//  */
// export interface BaseStackConfig {
//   /** Stack name */
//   name: string;
//   /** Deployment stage */
//   stage: Environment;
//   /** PR number for experimental deployments */
//   prNumber?: string;
//   /** Whether this is an experimental deployment */
//   isExperimental: boolean;
// }


// // src/utils/stack-utils.ts

// export class StackUtils {
//   /**
//    * Determines if a deployment is experimental based on PR number
//    */
//   static isExperimentalDeployment(prNumber?: string): boolean {
//     return !!prNumber;
//   }

//   /**
//    * Gets stack prefix based on deployment type
//    */
//   static getStackPrefix(stage: Environment, prNumber?: string): string {
//     return prNumber ? `pr-${prNumber}` : stage;
//   }

//   /**
//    * Gets stack removal policy based on deployment type
//    */
//   static getRemovalPolicy(isExperimental: boolean): cdk.RemovalPolicy {
//     return isExperimental ? cdk.RemovalPolicy.DESTROY : cdk.RemovalPolicy.RETAIN;
//   }

//   /**
//    * Gets common tags for all resources
//    */
//   static getCommonTags(config: BaseStackConfig): { [key: string]: string } {
//     return {
//       Environment: config.stage,
//       Service: config.name,
//       ManagedBy: 'CDK',
//       ...(config.isExperimental && {
//         PR: config.prNumber!,
//         Temporary: 'true',
//         ExperimentalDeployment: 'true',
//       }),
//     };
//   }
// }

// // SSM Parameter Store Helper Function
// import * as AWS from 'aws-sdk';
// const ssm = new AWS.SSM();

// export async function getParameterValue(parameterName: string): Promise<string> {
//   try {
//     const result = await ssm.getParameter({
//       Name: parameterName,
//       WithDecryption: true,
//     }).promise();

//     if (!result.Parameter || !result.Parameter.Value) {
//       throw new Error(`Parameter ${parameterName} not found in SSM Parameter Store`);
//     }

//     return result.Parameter.Value;
//   } catch (error) {
//     throw new Error(`Failed to get parameter ${parameterName}: `);
//   }
// }
