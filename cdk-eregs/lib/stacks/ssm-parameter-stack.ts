
import * as cdk from 'aws-cdk-lib';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';

export interface SsmParameterStackProps extends cdk.StackProps {
  stage: string;
}

export class SsmParameterStack extends cdk.Stack {
  public readonly ssmParameters: Record<string, string>;

  constructor(scope: Construct, id: string, props: SsmParameterStackProps) {
    super(scope, id, props);

    this.ssmParameters = {
      vpcId: ssm.StringParameter.valueForStringParameter(this, `/account_vars/vpc/id`),
      iamPath: ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/path'),
      permissionsBoundaryPolicy: ssm.StringParameter.valueForStringParameter(
        this,
        '/account_vars/iam/permissions_boundary_policy'
      ),
      logLevel: ssm.StringParameter.valueForStringParameter(this, '/eregulations/text_extractor/log_level'),
      httpUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
      httpPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
    };
  }
}
// import * as cdk from 'aws-cdk-lib';
// import * as ssm from 'aws-cdk-lib/aws-ssm';
// import { Construct } from 'constructs';

// export interface SsmParameterStackProps extends cdk.StackProps {
//   stage?: string;
// }

// export class SsmParameterStack extends cdk.Stack {
//   public readonly ssmParameters: { [key: string]: ssm.StringParameter };

//   constructor(scope: Construct, id: string, props?: SsmParameterStackProps) {
//     super(scope, id, props);

//     // Example SSM Parameters - Replace with actual values
//     this.ssmParameters = {
//       iamPath: ssm.StringParameter.valueForStringParameter(this, '/account_vars/iam/path'),
//       permissionsBoundaryPolicy: ssm.StringParameter.valueForStringParameter(
//         this,
//         '/account_vars/iam/permissions_boundary_policy'
//       ),
//       logLevel: ssm.StringParameter.valueForStringParameter(this, '/eregulations/text_extractor/log_level'),
//       httpUser: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/user'),
//       httpPassword: ssm.StringParameter.valueForStringParameter(this, '/eregulations/http/password'),
//     };
//   }

//   public async fetchParameters(): Promise<void> {
//     // Functionality to prefetch parameters for ensuring that they are available before deployment
//   }
// }
