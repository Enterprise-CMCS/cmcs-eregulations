<<<<<<< HEAD
// lib/utils/environment.ts
import { Environment, EnvironmentContext, VALID_ENVIRONMENTS, isValidEnvironment } from './environments';

/**
 * Validates the environment and constructs the context based on deployment details.
 * @param env - The target environment (e.g., 'dev', 'prod').
 * @param ephemeralId - Optional ID for ephemeral environments.
 * @param branch - Git branch (used for context in CI/CD).
 * @param prNumber - PR number for ephemeral deployments.
 * @returns EnvironmentContext - Validated environment context.
 */
export function validateEnvironmentContext(
  env?: string,
  ephemeralId?: string,
  branch?: string,
  prNumber?: string
): EnvironmentContext {
  const environment = validateEnvironment(env);

  if (prNumber && !ephemeralId) {
    throw new Error('Ephemeral ID is required when a PR number is provided');
  }

  if (ephemeralId) {
    validateEphemeralId(ephemeralId);
  }

  return { environment, ephemeralId, branch, prNumber };
}

/**
 * Checks if the provided environment is valid and returns it.
 * @param env - Environment as a string.
 * @returns Environment - Valid environment constant.
 */
export function validateEnvironment(env?: string): Environment {
  const environment = (env || 'dev').toLowerCase() as Environment;

  if (!isValidEnvironment(environment)) {
    throw new Error(`Invalid environment: ${environment}. Must be one of: ${VALID_ENVIRONMENTS.join(', ')}`);
  }

  return environment;
}

/**
 * Validates the format of an ephemeral ID.
 * @param ephemeralId - Ephemeral environment identifier.
 */
export function validateEphemeralId(ephemeralId: string): void {
  if (ephemeralId.length > 20) throw new Error('Ephemeral ID cannot exceed 20 characters');
  if (!/^[a-z0-9-]+$/.test(ephemeralId)) throw new Error('Ephemeral ID must contain only lowercase letters, numbers, and hyphens');
  if (!ephemeralId.startsWith('eph-')) throw new Error('Ephemeral ID must start with "eph-"');
}

/**
 * Generates tags for the environment.
 * @param environment - The deployment environment.
 * @param projectName - Name of the project.
 * @param serviceName - Name of the service.
 * @param ephemeralId - Ephemeral ID, if any.
 * @returns Record<string, string> - Key-value pairs for tags.
 */
export function getEnvironmentTags(
  environment: Environment,
  projectName: string,
  serviceName: string,
  ephemeralId?: string
): Record<string, string> {
  const tags: Record<string, string> = {
    Environment: environment,
    Project: projectName,
    Service: serviceName,
  };

  if (ephemeralId) {
    tags.EphemeralId = ephemeralId;
    tags.EnvironmentType = 'ephemeral';
  } else {
    tags.EnvironmentType = 'permanent';
  }

  return tags;
=======
import * as cdk from 'aws-cdk-lib';
import { IamPathAspect } from '../lib/constructs/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/constructs/iam-permissions-boundary-aspect';

export class EnvironmentConfig {
  public readonly stackPrefix: string;
  public readonly isExperimental: boolean;
  public readonly accountId: string;
  public readonly region: string;
  public readonly iamPermissionsBoundaryArn: string;
  public readonly iamPath: string;

  constructor(
    public readonly branchName: string,
    public readonly account?: string,
    public readonly prNumber?: string
  ) {
    // Determine if this is an experimental (PR) environment
    this.isExperimental = branchName.startsWith('pr-') || branchName.startsWith('PR-');

    // Set the stack prefix based on whether it's experimental or not
    this.stackPrefix = this.isExperimental ? `PR-${prNumber}` : this.getEnvironmentFromBranch();

    // Get account ID and region based on the environment
    const { accountId, region } = this.getAccountAndRegion();
    this.accountId = accountId;
    this.region = region;

    // Set IAM path and permissions boundary ARN based on the environment
    this.iamPath = this.isExperimental ? '/delegatedadmin/developer/' : '/delegatedadmin/developer/';
    this.iamPermissionsBoundaryArn = this.isExperimental
      ? `arn:aws:iam::${account}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy`
      : `arn:aws:iam::${account}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy`;
  }

  // Determine the environment based on the branch name
  private getEnvironmentFromBranch(): string {
    switch (this.branchName.toLowerCase()) {
      case 'main':
        return 'dev';
      case 'val':
        return 'val';
      case 'prod':
        return 'prod';
      case 'dev':
        return 'dev';
      default:
        // If the branch name does not match any of the known environments, default to 'dev'
        return 'dev';
    }
  }
  // Get the AWS account ID and region for the current environment
  private getAccountAndRegion(): { accountId: string; region: string } {
    switch (this.getEnvironmentFromBranch()) {
      case 'dev':
        return { accountId: '910670052382', region: 'us-east-1' };
      case 'val':
        return { accountId: '222222222222', region: 'us-east-1' };
      case 'prod':
        return { accountId: '333333333333', region: 'us-east-1' };
      default:
        // Experimental environments use dev account by default
        return { accountId: '111111111111', region: 'us-east-1' };
    }
  }

  // Lambda function configuration
  get lambdaConfig() {
    return {
      memorySize: this.isExperimental ? 128 : 256,
      timeout: cdk.Duration.seconds(this.isExperimental ? 30 : 60),
    };
  }

  // API Gateway configuration
  get apiGatewayConfig() {
    return {
      deployOptions: {
        stageName: this.isExperimental ? 'exp' : 'prod',
        tracingEnabled: !this.isExperimental,
      },
    };
  }

  // IAM configuration
  get iamConfig() {
    return {
      path: this.iamPath,
      permissionsBoundary: this.iamPermissionsBoundaryArn,
    };
  }

  // Add Aspects to the application
  public applyAspects(app: cdk.App) {
    cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(this.iamPermissionsBoundaryArn));
    cdk.Aspects.of(app).add(new IamPathAspect(this.iamPath));
  }
>>>>>>> main
}
