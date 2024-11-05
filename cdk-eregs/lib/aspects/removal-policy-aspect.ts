// lib/aspects/removal-policy-aspect.ts
import * as cdk from 'aws-cdk-lib';
import { IConstruct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

/**
 * An aspect that manages removal policies for resources in ephemeral environments.
 * When applied to ephemeral environments (like PR previews), this aspect:
 * - Protects database resources from deletion
 * - Sets all other resources to be destroyed on cleanup
 * 
 * @example
 * ```typescript
 * const app = new cdk.App();
 * const stageConfig = await StageConfig.create('dev', 'eph-123');
 * cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));
 * ```
 */
export class EphemeralRemovalPolicyAspect implements cdk.IAspect {
  private readonly stageConfig: StageConfig;

  /**
   * Patterns used to identify database resources that should be protected from deletion.
   * These patterns are matched case-insensitively against both the logical ID
   * and CloudFormation resource type.
   * 
   * @private
   * @readonly
   */
  private readonly protectedPatterns = [
    'database',    // Generic database resources
    'dbinstance',  // RDS instances
    'dbcluster',   // RDS clusters
    'aurora',      // Aurora-specific resources
    'rds'          // Other RDS-related resources
  ];

  /**
   * Creates a new instance of EphemeralRemovalPolicyAspect.
   * 
   * @param stageConfig - Configuration object containing environment information
   *                     and methods to determine if the environment is ephemeral
   */
  constructor(stageConfig: StageConfig) {
    this.stageConfig = stageConfig;
  }

  /**
   * Visits each construct in the CDK app and applies the appropriate removal policy.
   * For ephemeral environments:
   * - Database resources are protected (retain)
   * - All other resources are marked for deletion (destroy)
   * 
   * This method is called automatically by the CDK framework for each construct
   * when the aspect is added to the app or stack.
   * 
   * @param node - The construct being visited
   */
  visit(node: IConstruct): void {
    // Skip if not in ephemeral environment or not a CloudFormation resource
    if (!this.stageConfig.isEphemeral() || !(node instanceof cdk.CfnResource)) {
      return;
    }

    const logicalId = node.node.path;
    const resourceType = node.cfnResourceType || '';

    // Check if this is a database resource that should be protected
    const isDatabaseResource = this.protectedPatterns.some(pattern => 
      logicalId.toLowerCase().includes(pattern) || 
      resourceType.toLowerCase().includes(pattern)
    );

    if (!isDatabaseResource) {
      // Set non-database resources to be destroyed
      node.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
      
      // Only log during destroy operations
      if (this.isDestroyOperation()) {
        this.logResourcePolicy(logicalId, resourceType, true);
      }
    } else if (this.isDestroyOperation()) {
      // Log protected resources only during destroy
      this.logResourcePolicy(logicalId, resourceType, false);
    }
  }

  /**
   * Determines if the current CDK operation is a destroy operation.
   * Checks command-line arguments for 'destroy' or 'remove' commands.
   * 
   * @private
   * @returns boolean - True if this is a destroy operation
   */
  private isDestroyOperation(): boolean {
    const argv = process.argv.join(' ').toLowerCase();
    return argv.includes('destroy') || argv.includes('remove');
  }

  /**
   * Logs information about resource removal policies when debug mode is enabled.
   * Only logs when CDK_DEBUG environment variable is set.
   * 
   * @private
   * @param logicalId - The logical ID of the resource
   * @param resourceType - The CloudFormation resource type
   * @param willBeDestroyed - Whether the resource will be destroyed
   * 
   * @example
   * Debug output format:
   * [dev] Resource will be destroyed: MyStack/MyBucket (AWS::S3::Bucket)
   * [dev] Resource protected: MyStack/MyDatabase (AWS::RDS::DBInstance)
   */
  private logResourcePolicy(
    logicalId: string, 
    resourceType: string, 
    willBeDestroyed: boolean
  ): void {
    if (process.env.CDK_DEBUG) {
      const action = willBeDestroyed ? 'will be destroyed' : 'protected';
      console.log(
        `[${this.stageConfig.environment}] Resource ${action}: ${logicalId} (${resourceType})`
      );
    }
  }
}

