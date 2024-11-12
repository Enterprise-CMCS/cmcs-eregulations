// lib/config/stack-definitions.ts
import { aws_lambda as lambda, aws_apigateway as apigateway } from 'aws-cdk-lib';
import { RedirectApiStack } from '../lib/stacks/redirect-stack';
// import { MaintenanceApiStack } from '../lib/stacks/maintenance-stack';
// import { SomeOtherStack } from '../stacks/some-other-stack';

/**
 * Enum-like constant for identifying stack types.
 */
export const StackType = {
  REDIRECT_API: 'redirect-api',
//   SOME_OTHER_STACK: 'some-other-stack',
} as const;

type StackTypeKeys = keyof typeof StackType;
export type StackTypeValues = typeof StackType[StackTypeKeys];

/**
 * Mapping from StackType to stack classes, allowing for flexible instantiation in StackFactory.
 */
export const stackClassMap = {
  [StackType.REDIRECT_API]: RedirectApiStack,
//   [StackType.SOME_OTHER_STACK]: SomeOtherStack,
} as const;

// Base configuration interface for common stack properties.
export interface BaseStackConfig {
  type: StackTypeValues;
  enabled: boolean;
}

// Configuration interface specific to the RedirectApiStack.
export interface RedirectApiConfig extends BaseStackConfig {
  type: typeof StackType.REDIRECT_API;
  lambdaConfig: {
    runtime: lambda.Runtime;
    memorySize: number;
    timeout: number;
    environment?: Record<string, string>;
  };
  apiConfig?: {
    binaryMediaTypes?: string[];
    endpointType?: apigateway.EndpointType;
    loggingLevel?: apigateway.MethodLoggingLevel;
  };
}

// Configuration interface specific to the SomeOtherStack.
// export interface SomeOtherStackConfig extends BaseStackConfig {
//   type: typeof StackType.SOME_OTHER_STACK;
//   otherConfig: {
//     someSetting: boolean;
//   };
// }

// Union type for all stack configurations.
// export type StackConfig = RedirectApiConfig | SomeOtherStackConfig;
export type StackConfig = RedirectApiConfig;

/**
 * Generates configuration for the RedirectApiStack based on environment.
 * @param environment - Deployment environment.
 * @param isEphemeral - Whether this is an ephemeral deployment.
 * @returns RedirectApiConfig - Configuration for RedirectApiStack.
 */
const getRedirectApiConfig = (environment: string, isEphemeral: boolean): RedirectApiConfig => ({
  type: StackType.REDIRECT_API,
  enabled: true,
  lambdaConfig: {
    runtime: lambda.Runtime.PYTHON_3_12,
    memorySize: isEphemeral ? 512 : 1024,
    timeout: 30,
    environment: { LOG_LEVEL: isEphemeral ? 'DEBUG' : 'INFO' },
  },
  apiConfig: {
    binaryMediaTypes: ['multipart/form-data', 'application/pdf'],
    endpointType: apigateway.EndpointType.EDGE,
    loggingLevel: isEphemeral ? apigateway.MethodLoggingLevel.INFO : apigateway.MethodLoggingLevel.ERROR,
  },
});

// const getSomeOtherStackConfig = (environment: string, isEphemeral: boolean): SomeOtherStackConfig => ({
//   type: StackType.SOME_OTHER_STACK,
//   enabled: environment === 'prod',
//   otherConfig: {
//     someSetting: isEphemeral,
//   },
// });

/**
 * Aggregates stack configurations for the given environment.
 * Easily extensible: add more stack configurations by including additional configuration functions.
 * @param environment - Target environment.
 * @param isEphemeral - Boolean flag for ephemeral environments.
 * @returns StackConfig[] - Array of stack configurations.
 */
export const getStackConfigs = (environment: string, isEphemeral: boolean): StackConfig[] => [
  getRedirectApiConfig(environment, isEphemeral),
//   getSomeOtherStackConfig(environment, isEphemeral),
  // Add additional stack configurations here
];
