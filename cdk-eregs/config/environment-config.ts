
// import * as cdk from 'aws-cdk-lib';
// import * as ssm from 'aws-cdk-lib/aws-ssm';
// import { Construct } from 'constructs';
// import { IamPathAspect } from '../lib/constructs/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/constructs/iam-permissions-boundary-aspect';

// export interface EnvironmentConfig {
//   stackPrefix: string;
//   accountId: string;
//   region: string;
//   stage: string;
//   isExperimental: boolean;
// }

// export interface SsmParameters {
//   vpcId: string;
//   iamPath: string;
//   permissionsBoundaryPolicy: string;
//   logLevel: string;
//   httpUser: string;
//   httpPassword: string;
//   acmCertArn: string;
// }

// export class EnvironmentStack extends cdk.Stack {
//   public readonly config: EnvironmentConfig;
//   public readonly ssmParameters: SsmParameters;

//   constructor(scope: Construct, id: string, props?: cdk.StackProps) {
//     super(scope, id, props);

//     // Initialize environment configuration
//     this.config = this.initializeConfig();
    
//     // Fetch SSM parameters
//     this.ssmParameters = this.fetchSsmParameters();

//     // Apply global aspects
//     this.applyGlobalAspects(scope);
//   }

//   private initializeConfig(): EnvironmentConfig {
//     const branchName = process.env.GITHUB_REF_NAME || 'main';
//     const prNumber = process.env.GITHUB_EVENT_NUMBER;
//     const isExperimental = branchName.startsWith('pr-') || branchName.startsWith('PR-');
//     const stage = this.getStageFromBranch(branchName);
//     const { accountId, region } = this.getAccountAndRegion(stage);

//     return {
//       stackPrefix: isExperimental ? `PR-${prNumber}` : stage,
//       accountId,
//       region,
//       stage,
//       isExperimental
//     };
//   }

//   private fetchSsmParameters(): SsmParameters {
//     return {
//       vpcId: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/account_vars/vpc/id'
//       ),
//       iamPath: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/account_vars/iam/path'
//       ),
//       permissionsBoundaryPolicy: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/account_vars/iam/permissions_boundary_policy'
//       ),
//       logLevel: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/eregulations/text_extractor/log_level'
//       ),
//       httpUser: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/eregulations/http/user'
//       ),
//       httpPassword: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/eregulations/http/password'
//       ),
//       acmCertArn: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/eregulations/acm-cert-arn'
//       )
//     };
//   }

//   private getStageFromBranch(branchName: string): string {
//     const stageMap: { [key: string]: string } = {
//       main: 'dev',
//       val: 'val',
//       prod: 'prod',
//       dev: 'dev'
//     };
//     return stageMap[branchName.toLowerCase()] || 'dev';
//   }

//   private getAccountAndRegion(stage: string): { accountId: string; region: string } {
//     const environments: { [key: string]: { accountId: string; region: string } } = {
//       dev: { accountId: '009160033411', region: 'us-east-1' },
//       val: { accountId: '222222222222', region: 'us-east-1' },
//       prod: { accountId: '333333333333', region: 'us-east-1' }
//     };
//     return environments[stage] || environments.dev;
//   }

//   private applyGlobalAspects(scope: Construct): void {
//     const permissionsBoundaryArn = `arn:aws:iam::${this.config.accountId}:policy${this.ssmParameters.permissionsBoundaryPolicy}`;
//     cdk.Aspects.of(scope).add(new IamPermissionsBoundaryAspect(permissionsBoundaryArn));
//     cdk.Aspects.of(scope).add(new IamPathAspect(this.ssmParameters.iamPath));
//   }

//   // Helper methods for stack configuration
//   public getLambdaConfig() {
//     return {
//       memorySize: this.config.isExperimental ? 128 : 256,
//       timeout: cdk.Duration.seconds(this.config.isExperimental ? 30 : 60),
//       environment: {
//         STAGE: this.config.stage,
//         LOG_LEVEL: this.ssmParameters.logLevel
//       }
//     };
//   }

//   public getApiGatewayConfig() {
//     return {
//       deployOptions: {
//         stageName: this.config.isExperimental ? 'exp' : this.config.stage,
//         tracingEnabled: !this.config.isExperimental,
//         loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
//         dataTraceEnabled: true,
//         metricsEnabled: true
//       }
//     };
//   }
// }
// import * as cdk from 'aws-cdk-lib';
// import * as ssm from 'aws-cdk-lib/aws-ssm';
// import { Construct } from 'constructs';
// import { IamPathAspect } from '../lib/constructs/iam-path';
// import { IamPermissionsBoundaryAspect } from '../lib/constructs/iam-permissions-boundary-aspect';

// export interface EnvironmentConfig {
//   stackPrefix: string;
//   accountId: string;
//   region: string;
//   stage: string;
//   isExperimental: boolean;
// }

// export interface SsmParameters {
//   vpcId: string;
//   iamPath: string;
//   permissionsBoundaryPolicy: string;
//   logLevel: string;
//   httpUser: string;
//   httpPassword: string;
//   acmCertArn: string;
// }

// export class EnvironmentStack extends cdk.Stack {
//   public readonly config: EnvironmentConfig;
//   public readonly ssmParameterOutputs: Record<string, cdk.CfnOutput>;

//   constructor(scope: Construct, id: string, props?: cdk.StackProps) {
//     super(scope, id, props);

//     // Initialize environment configuration
//     this.config = this.initializeConfig();
    
//     // Create outputs for SSM parameters
//     this.ssmParameterOutputs = this.createSsmParameterOutputs();

//     // Apply global aspects
//     this.applyGlobalAspects(scope);
//   }

//   private initializeConfig(): EnvironmentConfig {
//     const branchName = process.env.GITHUB_REF_NAME || 'main';
//     const prNumber = process.env.GITHUB_EVENT_NUMBER;
//     const isExperimental = branchName.startsWith('pr-') || branchName.startsWith('PR-');
//     const stage = this.getStageFromBranch(branchName);
//     const { accountId, region } = this.getAccountAndRegion(stage);

//     return {
//       stackPrefix: isExperimental ? `PR-${prNumber}` : stage,
//       accountId,
//       region,
//       stage,
//       isExperimental
//     };
//   }

//   private createSsmParameterOutputs(): Record<string, cdk.CfnOutput> {
//     const parameterMap = {
//       vpcId: '/account_vars/vpc/id',
//       iamPath: '/account_vars/iam/path',
//       permissionsBoundaryPolicy: '/account_vars/iam/permissions_boundary_policy',
//       logLevel: '/eregulations/text_extractor/log_level',
//       httpUser: '/eregulations/http/user',
//       httpPassword: '/eregulations/http/password',
//       acmCertArn: '/eregulations/acm-cert-arn'
//     };

//     const outputs: Record<string, cdk.CfnOutput> = {};

//     for (const [key, paramPath] of Object.entries(parameterMap)) {
//       const paramValue = ssm.StringParameter.valueForStringParameter(this, paramPath);
//       outputs[key] = new cdk.CfnOutput(this, `SSMOutput${key}`, {
//         value: paramValue,
//         exportName: `${this.config.stackPrefix}-${key}`
//       });
//     }

//     return outputs;
//   }

//   private getStageFromBranch(branchName: string): string {
//     const stageMap: { [key: string]: string } = {
//       main: 'dev',
//       val: 'val',
//       prod: 'prod',
//       dev: 'dev'
//     };
//     return stageMap[branchName.toLowerCase()] || 'dev';
//   }

//   private getAccountAndRegion(stage: string): { accountId: string; region: string } {
//     const environments: { [key: string]: { accountId: string; region: string } } = {
//       dev: { accountId: '009160033411', region: 'us-east-1' },
//       val: { accountId: '222222222222', region: 'us-east-1' },
//       prod: { accountId: '333333333333', region: 'us-east-1' }
//     };
//     return environments[stage] || environments.dev;
//   }

//   private applyGlobalAspects(scope: Construct): void {
//     cdk.Aspects.of(scope).add(
//       new IamPermissionsBoundaryAspect(
//         `arn:aws:iam::${this.config.accountId}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy`
//       )
//     );
//     cdk.Aspects.of(scope).add(new IamPathAspect('/delegatedadmin/developer/'));
//   }

//   public getSsmValue(key: keyof SsmParameters): string {
//     return cdk.Fn.importValue(`${this.config.stackPrefix}-${key}`);
//   }
// }
import * as cdk from 'aws-cdk-lib';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';

interface EnvironmentConfigProps extends cdk.StackProps {
  environment: string;
}

export class EnvironmentConfigStack extends cdk.Stack {
  public readonly config: { [key: string]: any };

  constructor(scope: Construct, id: string, props: EnvironmentConfigProps) {
    super(scope, id, props);

    const { environment } = props;

    // Load configuration from Parameter Store
    this.config = this.loadConfigFromParameterStore(environment);
  }

  private loadConfigFromParameterStore(environment: string): { [key: string]: any } {
    const parameters: { [key: string]: any } = {};

    // List of parameter keys that are needed for the environment
    const parameterKeys = [
      '/account_vars/vpc/id',
    //   `/app/config/${environment}/api-endpoint`,
    //   `/app/config/${environment}/feature-toggle`,
    ];

    parameterKeys.forEach((paramKey) => {
      const paramValue = ssm.StringParameter.valueForStringParameter(this, paramKey);
      parameters[paramKey] = paramValue;
    });

    return parameters;
  }
}