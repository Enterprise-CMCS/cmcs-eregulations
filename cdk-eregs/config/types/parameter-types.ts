// src/config/ssm-parameters.ts
import { Environment } from '../types/config-types';
import { Construct } from 'constructs';
import * as ssm from 'aws-cdk-lib/aws-ssm';
/**
 * Definition for an SSM parameter including validation and transformation
 */
export interface SSMParameterDefinition {
  /** SSM parameter path */
  path: string;
  /** Whether the parameter is required */
  required: boolean;
  /** Description of the parameter's purpose */
  description: string;
  /** Default value if parameter is not found */
  defaultValue?: string;
  /** Function to transform the parameter value */
  transform?: (value: string) => any;
  /** Function to validate the parameter value */
  validate?: (value: any) => boolean;
}

/** Grouping of related SSM parameters */
export type SSMParameterGroup = Record<string, SSMParameterDefinition>;

/**
 * Centralized SSM parameter definitions for all services
 * When adding new parameters:
 * 1. Add the parameter definition to the appropriate group
 * 2. Ensure proper validation and transformation if needed
 * 3. Add proper JSDoc comments for clarity
 */
export const SSM_PARAMETERS = {
  /**
   * Base infrastructure parameters used across all services
   */
  BASE: {
    /** IAM role path prefix */
    IAM_PATH: {
      path: '/account_vars/iam/path',
      required: true,
      description: 'IAM path prefix for all IAM resources',
      defaultValue: '/',
      validate: (value: string) => value.startsWith('/'),
    },
    /** IAM permissions boundary policy ARN */
    PERMISSIONS_BOUNDARY: {
      path: '/account_vars/iam/permissions_boundary_policy',
      required: true,
      description: 'ARN of the permissions boundary policy',
      validate: (value: string) => value.startsWith('arn:aws:iam::'),
    },
    /** IAM role name prefix */
    IAM_ROLE_PREFIX: {
      path: '/account_vars/iam/role_prefix',
      required: false,
      description: 'Prefix for IAM role names',
      defaultValue: '',
    },
  } as SSMParameterGroup,

  /**
   * VPC and networking parameters
   */
  VPC: {
    /** VPC ID */
    ID: {
      path: '/account_vars/vpc/id',
      required: true,
      description: 'VPC ID for the environment',
      validate: (value: string) => value.startsWith('vpc-'),
    },
    /** Private subnet IDs */
    PRIVATE_SUBNETS: {
      path: '/account_vars/vpc/private_subnet_ids',
      required: true,
      description: 'Comma-separated list of private subnet IDs',
      transform: (value: string) => value.split(','),
      validate: (value: string[]) => 
        value.length > 0 && value.every(id => id.startsWith('subnet-')),
    },
    /** Security group IDs */
    SECURITY_GROUPS: {
      path: '/account_vars/vpc/security_group_ids',
      required: true,
      description: 'Comma-separated list of security group IDs',
      transform: (value: string) => value.split(','),
      validate: (value: string[]) => 
        value.length > 0 && value.every(id => id.startsWith('sg-')),
    },
  } as SSMParameterGroup,

  /**
   * Redirect service specific parameters
   */
  REDIRECT: {
    /** Target domain for redirects */
    TARGET_DOMAIN: {
      path: '/services/redirect/target_domain',
      required: true,
      description: 'Target domain for redirects',
      validate: (value: string) => value.includes('.'),
    },
    /** Cache TTL in seconds */
    CACHE_TTL: {
      path: '/services/redirect/cache_ttl',
      required: false,
      description: 'Cache TTL in seconds',
      defaultValue: '3600',
      transform: (value: string) => parseInt(value, 10),
      validate: (value: number) => value > 0,
    },
  } as SSMParameterGroup,
  
  /**
   * Authentication service specific parameters
   * Example of how to add new service parameters
   */
  AUTH: {
    /** Cognito User Pool ID */
    USER_POOL_ID: {
      path: '/services/auth/user_pool_id',
      required: true,
      description: 'Cognito User Pool ID',
      validate: (value: string) => value.startsWith('us-east-1_'),
    },
    /** JWT token expiration in hours */
    TOKEN_EXPIRATION: {
      path: '/services/auth/token_expiration_hours',
      required: false,
      description: 'JWT token expiration time in hours',
      defaultValue: '24',
      transform: (value: string) => parseInt(value, 10),
      validate: (value: number) => value > 0 && value <= 168, // Max 1 week
    },
  } as SSMParameterGroup,
} as const;

/**
 * Parameter Store utility class for managing SSM parameters
 * Handles caching, validation, and transformation of parameters
 */
export class ParameterStore {
    private static instance: ParameterStore;
    private parameterCache: Map<string, any> = new Map();
  
    private constructor(
      private readonly scope: Construct,
      private readonly stage: Environment
    ) {}
  
    /**
     * Gets singleton instance of ParameterStore
     * @param scope CDK construct scope
     * @param stage Deployment stage
     */
    public static getInstance(scope: Construct, stage: Environment): ParameterStore {
      if (!this.instance) {
        this.instance = new ParameterStore(scope, stage);
      }
      return this.instance;
    }
  
    /**
     * Gets a parameter value with caching, validation, and transformation
     * @param groupKey Parameter group key (e.g., 'BASE', 'REDIRECT')
     * @param paramKey Parameter key within the group
     * @returns Parsed and validated parameter value
     */
    public getParameter<T = string>(groupKey: keyof typeof SSM_PARAMETERS, paramKey: string): T {
      const group = SSM_PARAMETERS[groupKey];
      const definition = group[paramKey];
      
      if (!definition) {
        throw new Error(`Parameter ${paramKey} not found in group ${groupKey}`);
      }
  
      const paramPath = this.getParameterPath(definition.path);
      
      if (this.parameterCache.has(paramPath)) {
        return this.parameterCache.get(paramPath);
      }
  
      try {
        const value = ssm.StringParameter.valueForStringParameter(
          this.scope,
          paramPath
        );
  
        const transformedValue = definition.transform 
          ? definition.transform(value) 
          : value;
  
        if (definition.validate && !definition.validate(transformedValue)) {
          throw new Error(
            `Parameter ${paramPath} (${groupKey}.${paramKey}) failed validation`
          );
        }
  
        this.parameterCache.set(paramPath, transformedValue);
        return transformedValue;
      } catch (error: unknown) {
        if (error instanceof Error && error.name === 'ParameterNotFound' && !definition.required) {
          const defaultValue = definition.defaultValue;
          if (defaultValue !== undefined) {
            const transformedDefault = definition.transform 
              ? definition.transform(defaultValue) 
              : defaultValue;
            this.parameterCache.set(paramPath, transformedDefault);
            return transformedDefault;
          }
        }
        const errorMessage = error instanceof Error ? error.message : String(error);
        throw new Error(
          `Failed to load parameter ${paramPath} (${groupKey}.${paramKey}): ${errorMessage}`
        );
      }
    }
  
    /**
     * Gets the environment-specific parameter path
     * @param basePath Base parameter path
     * @returns Stage-specific parameter path
     */
    private getParameterPath(basePath: string): string {
      return basePath.replace('/services', `/services/${this.stage}`);
    }
  }