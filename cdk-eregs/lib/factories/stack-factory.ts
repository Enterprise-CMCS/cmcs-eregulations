// lib/factories/stack-factory.ts

import * as cdk from 'aws-cdk-lib';
import { StackConfig, stackClassMap } from '../../config/stack-definition';
import { StageConfig } from '../../config/stage-config';
import { RedirectApiStackProps } from '../stacks/redirect-stack';

/**
 * Factory class responsible for creating and configuring stacks based on provided configurations.
 * This class allows the creation of multiple stack types by mapping configurations to specific stack classes,
 * making it flexible and extendable for additional infrastructure components as needed.
 */
export class StackFactory {
  private readonly app: cdk.App;
  private readonly stageConfig: StageConfig;

  /**
   * Constructs a new StackFactory instance.
   * @param app - The CDK app context used for defining AWS resources.
   * @param stageConfig - Configuration details for the current deployment stage (e.g., 'dev', 'prod').
   *                       Contains essential environment-specific information, such as IAM paths and permissions.
   */
  constructor(app: cdk.App, stageConfig: StageConfig) {
    this.app = app;
    this.stageConfig = stageConfig;
  }

  /**
   * Creates and returns a CDK Stack instance based on the specified stack configuration.
   * This method checks if the stack is enabled in the configuration, generates a unique stack name,
   * and instantiates the stack with appropriate properties.
   *
   * @param stackConfig - The configuration object for the stack to be created, including its type and specific settings.
   * @returns cdk.Stack | null - Returns the created stack if enabled, or null if the stack is not enabled in the configuration.
   */
  public createStack(stackConfig: StackConfig): cdk.Stack | null {
    if (!stackConfig.enabled) return null; // Skip creation if the stack is disabled

    const StackClass = stackClassMap[stackConfig.type];
    const stackName = this.stageConfig.getStackName(stackConfig.type); // Generate unique stack name based on conventions

    // Generate stack-specific properties and pass relevant stage configuration properties
    const stackProps = this.getStackProps(stackConfig);

    // Instantiate and return the stack using the appropriate class and properties
    return new StackClass(this.app, stackName, stackProps);
  }

  /**
   * Generates stack-specific properties for instantiation, depending on the stack type.
   * This method constructs a base property set common to all stacks (e.g., stage, IAM path, permissions boundary),
   * and then adds additional properties specific to the stack type.
   *
   * The use of a switch-case structure allows easy extension: simply add new cases for additional stack types.
   *
   * @param stackConfig - Configuration object for the stack, detailing the specific settings required for this stack type.
   * @returns RedirectApiStackProps - A typed set of properties required for the stack's instantiation.
   */
  private getStackProps(stackConfig: StackConfig): RedirectApiStackProps {
    // Shared base properties for all stacks, ensuring consistent IAM paths, permissions, and project naming
    const baseProps = {
      stage: this.stageConfig.environment,  // Stage environment (e.g., 'dev', 'prod'), aligned with `stage` naming conventions
      iamPath: this.stageConfig.iamPath,    // IAM path setting for resource organization
      permissionsBoundaryArn: this.stageConfig.permissionsBoundaryArn,  // Permissions boundary for IAM roles
      appName: StageConfig.projectName,     // Project name, applied to all stacks for consistent naming
    };

    switch (stackConfig.type) {
      case 'redirect-api':
        return {
          ...baseProps,
          lambdaConfig: stackConfig.lambdaConfig,   // Lambda-specific configuration settings
          apiConfig: stackConfig.apiConfig ?? {},   // Optional API Gateway configuration, defaults to an empty object
        } as RedirectApiStackProps;

      // Example of additional stack case, demonstrating extensibility:
      // case 'data-pipeline':
      //   return {
      //     ...baseProps,
      //     pipelineConfig: stackConfig.pipelineConfig, // Example property specific to DataPipelineStack
      //   } as DataPipelineStackProps;

      default:
        throw new Error(`Unsupported stack type: ${stackConfig.type}`);
    }
  }
}

