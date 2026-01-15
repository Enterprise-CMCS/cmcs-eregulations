import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_wafv2 as wafv2 } from 'aws-cdk-lib';

export interface WafAssociationStackProps extends cdk.StackProps {
  /** The ARN of the API Gateway stage to associate with the WAF */
  apiStageArn: string;
  /** The ARN of the WAF WebACL */
  webAclArn: string;
}

export class WafAssociationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: WafAssociationStackProps) {
    super(scope, id, props);

    new wafv2.CfnWebACLAssociation(this, 'ApiGatewayWAFAssociation', {
        resourceArn: props.apiStageArn,
        webAclArn: props.webAclArn,
    });
  }
}
