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
}
