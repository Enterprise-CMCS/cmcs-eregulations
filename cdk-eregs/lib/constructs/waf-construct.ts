import * as cdk from 'aws-cdk-lib';
import { aws_wafv2 as wafv2 } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

export class WafConstruct extends Construct {
  public readonly webAcl: wafv2.CfnWebACL;

  constructor(scope: Construct, id: string, stageConfig: StageConfig) {
    super(scope, id);

    this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
      defaultAction: { allow: {} },
      scope: 'REGIONAL',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: stageConfig.getResourceName('api-metrics'),
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: stageConfig.getResourceName('allow-usa-territories'),
          priority: 0,
          statement: {
            geoMatchStatement: {
              countryCodes: ['US', 'GU', 'PR', 'VI', 'MP', 'AS', 'UM'],
            },
          },
          action: { allow: {} },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: stageConfig.getResourceName('usa-territories-metric'),
            sampledRequestsEnabled: true,
          },
        },
      ],
    });
  }
}