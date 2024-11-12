// lib/types/environment.ts

/**
 * Defines the valid deployment environments in the project.
 */
export type Environment = 'dev' | 'val' | 'prod' | 'ephemeral';

/**
 * List of valid environments for validation purposes.
 */
export const VALID_ENVIRONMENTS: Environment[] = ['dev', 'val', 'prod', 'ephemeral'];

/**
 * Helper function to check if the provided environment is within the list of valid environments.
 * @param env - The environment string to check.
 * @returns boolean - True if the environment is valid; otherwise, false.
 */
export function isValidEnvironment(env: string): env is Environment {
    return VALID_ENVIRONMENTS.includes(env as Environment);
  }
/**
 * Interface representing the context for a deployment environment.
 * This includes standard environment details as well as ephemeral-specific properties.
 */
export interface EnvironmentContext {
  /**
   * The primary environment, e.g., 'dev', 'val', 'prod', 'ephemeral'.
   */
  environment: Environment;

  /**
   * Optional ID for ephemeral environments, often derived from PR numbers.
   */
  ephemeralId?: string;

  /**
   * Name of the branch being deployed, useful in CI/CD workflows.
   */
  branch?: string;

  /**
   * Pull Request number, used to create unique identifiers for ephemeral deployments.
   */
  prNumber?: string;
}