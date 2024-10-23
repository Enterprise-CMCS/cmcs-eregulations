// bin/cdk-eregs.ts
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { RedirectStack } from '../lib/stacks/redirect-stack';
import { StaticAssetsStack } from '../lib/stacks/static-asset-construct';
import { EnvironmentStack } from '../config/environment-config';
import { SsmParameters } from '../config/environment-config';


async function main() {
  const app = new cdk.App({
    defaultStackSynthesizer: new cdk.DefaultStackSynthesizer({
      qualifier: 'one',
      cloudFormationExecutionRole: 'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-cfn-exec-role-009160033411-us-east-1',
      deployRoleArn: 'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-deploy-role-009160033411-us-east-1',
      fileAssetPublishingRoleArn: 'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-file-publishing-role-009160033411-us-east-1',
      imageAssetPublishingRoleArn: 'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-image-publishing-role-009160033411-us-east-1',
      lookupRoleArn: 'arn:aws:iam::009160033411:role/delegatedadmin/developer/cdk-one-lookup-role-009160033411-us-east-1',
    })
  });

  // Create environment stack first
  const envStack = new EnvironmentStack(app, 'EnvironmentStack');
  const { config, ssmParameters } = envStack;

  // Create application stacks with environment configuration
  new RedirectStack(app, `${config.stackPrefix}-RedirectStack`, {
    env: {
      account: config.accountId,
      region: config.region
    },
    ssmParameters,
    lambdaConfig: envStack.getLambdaConfig(),
    apiGatewayConfig: envStack.getApiGatewayConfig()
  });

  new StaticAssetsStack(app, `${config.stackPrefix}-StaticAssets`, {
    env: {
      account: config.accountId,
      region: config.region
    },
    config,
    ssmParameters
  });

  app.synth();
}

main().catch(error => {
  console.error('Error during deployment:', error);
  process.exit(1);
});