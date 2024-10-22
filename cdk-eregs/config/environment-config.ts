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
      ? 'arn:aws:iam::009160033411:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy'
      : 'arn:aws:iam::009160033411:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy';
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
        return { accountId: '009160033411', region: 'us-east-1' };
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
}
