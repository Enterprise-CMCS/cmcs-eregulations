// lib/config/stage-config.ts
import { getParameterValue } from '../utils/parameter-store';

/**
 * AWS service identifiers for resource naming
 */
const AWS_SERVICES = {
  LAMBDA: 'lambda',
  API_GATEWAY: 'api-gateway',
  CLOUDWATCH: 'cloudwatch',
  S3: 's3',
  DYNAMODB: 'dynamodb',
  SNS: 'sns',
  SQS: 'sqs',
  EVENTS: 'events',
  TEXTRACT: 'textract',
} as const;

/**
 * Configuration class that provides environment-specific settings and resource naming.
 * Handles both regular (dev, prod) and ephemeral (PR-based) environments.
 *
 * @example
 * ```typescript
 * // Regular environment
 * const config = await StageConfig.create('dev', undefined, synthesizerConfig.iamPermissionsBoundary);
 * config.aws.lambda('function')  // → /aws/lambda/a1m-eregs-dev-function
 *
 * // PR environment
 * const config = await StageConfig.create('dev', 'eph-123', synthesizerConfig.iamPermissionsBoundary);
 * config.aws.lambda('function')  // → /aws/lambda/a1m-eregs-eph-123-function
 * ```
 */
export class StageConfig {
  /**
   * Project name used across all environments
   */
  public static readonly projectName = 'a1m-eregs';

  /**
   * Creates a new StageConfig instance
   * @param environment - Deployment environment (e.g., 'dev', 'prod')
   * @param ephemeralId - Optional ephemeral environment ID (e.g., 'eph-123')
   * @param synthesizerPermissionsBoundary - IAM permissions boundary from synthesizer config
   */
  public static async create(
    environment: string,
    ephemeralId?: string,
    synthesizerPermissionsBoundary?: string
  ): Promise<StageConfig> {
    // Only fetch IAM path from parameter store
    const iamPath = await getParameterValue('/account_vars/iam/path');

    // Use synthesizer boundary if provided, otherwise throw error
    if (!synthesizerPermissionsBoundary) {
      throw new Error('Permissions boundary must be provided from synthesizer config');
    }

    return new StageConfig(
      environment,
      iamPath,
      synthesizerPermissionsBoundary,
      ephemeralId
    );
  }

  private constructor(
    public readonly environment: string,
    public readonly iamPath: string,
    public readonly permissionsBoundaryArn: string,
    private readonly ephemeralId?: string
  ) {
    // Add validation if needed
    if (!permissionsBoundaryArn) {
      throw new Error('Permissions boundary ARN is required');
    }
  }

  public get stageName(): string {
    // If ephemeral environment exists use it, otherwise use environment
    return this.ephemeralId || this.environment;
  }

  public get databaseName(): string {
    return this.ephemeralId?.replace("-", "_") ?? 'eregs';
  }

  public isEphemeral(): boolean {
    return !!this.ephemeralId;
  }

  public getResourceName(resource: string): string {
    const environmentPart = this.ephemeralId || this.environment;
    return `${StageConfig.projectName}-${environmentPart}-${resource}`.toLowerCase();
  }

  public getStackTags(): Record<string, string> {
    const tags: Record<string, string> = {
      Environment: this.environment,
      Project: StageConfig.projectName,
      EnvironmentType: this.isEphemeral() ? 'ephemeral' : 'permanent',
    };

    if (this.ephemeralId) {
      tags.EphemeralId = this.ephemeralId;
    }

    // Add permission boundary as a tag for tracking
    tags.PermissionsBoundary = this.permissionsBoundaryArn.split('/').pop() || '';

    return tags;
  }

  // AWS service namespace remains the same
  public readonly aws = {
    service: (service: string, resource: string): string =>
      `/aws/${service}/${this.getResourceName(resource)}`,

    lambda: (resource: string): string =>
      this.aws.service(AWS_SERVICES.LAMBDA, resource),

    apiGateway: (resource: string): string =>
      this.aws.service(AWS_SERVICES.API_GATEWAY, resource),

    cloudwatch: (resource: string): string =>
      this.aws.service(AWS_SERVICES.CLOUDWATCH, resource),

    s3: (resource: string): string =>
      this.aws.service(AWS_SERVICES.S3, resource),

    dynamodb: (resource: string): string =>
      this.aws.service(AWS_SERVICES.DYNAMODB, resource),

    sns: (resource: string): string =>
      this.aws.service(AWS_SERVICES.SNS, resource),

    sqs: (resource: string): string =>
      this.aws.service(AWS_SERVICES.SQS, resource),

    events: (resource: string): string =>
      this.aws.service(AWS_SERVICES.EVENTS, resource),
  };
}
