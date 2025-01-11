import * as cdk from 'aws-cdk-lib';
import { aws_wafv2 as wafv2, aws_logs as logs } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

export class WafConstruct extends Construct {
  public readonly webAcl: wafv2.CfnWebACL;

  constructor(scope: Construct, id: string, stageConfig: StageConfig) {
    super(scope, id);

    // Create WAF ACL matching serverless configuration
    this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
      name: `APIGateway-eregs-allow-usa-plus-territories-${stageConfig.environment}`,
      defaultAction: { allow: {} },
      scope: 'REGIONAL',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: stageConfig.getResourceName('api-metrics'),
        sampledRequestsEnabled: true,
      },
      rules: [
        // Geo restriction rule exactly matching serverless.yml
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
        // Rate limiting rule
        {
          name: stageConfig.getResourceName('rate-limit'),
          priority: 1,
          statement: {
            rateBasedStatement: {
              limit: 2000,
              aggregateKeyType: 'IP',
            },
          },
          action: { block: {} },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: stageConfig.getResourceName('rate-limit-metric'),
            sampledRequestsEnabled: true,
          },
        },
        // AWS Managed Rule Sets
        {
          name: 'AWSManagedRulesCommonRuleSet',
          priority: 2,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesCommonRuleSet'
            }
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'AWSManagedRulesCommonRuleSetMetric',
            sampledRequestsEnabled: true
          }
        },
        {
          name: 'AWSManagedRulesKnownBadInputsRuleSet',
          priority: 3,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesKnownBadInputsRuleSet'
            }
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'AWSManagedRulesKnownBadInputsRuleSetMetric',
            sampledRequestsEnabled: true
          }
        }
      ]
    });

    // Create log group for WAF logs
    const logGroup = new logs.LogGroup(this, 'WafLogGroup', {
      logGroupName: stageConfig.getResourceName('waf-logs'),
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Configure WAF logging
    const loggingConfig = new wafv2.CfnLoggingConfiguration(this, 'WafLogging', {
      logDestinationConfigs: [logGroup.logGroupArn],
      resourceArn: this.webAcl.attrArn
    });

    // Add tags
    cdk.Tags.of(this).add('Name', `eregs-waf-${stageConfig.environment}`);
    cdk.Tags.of(this).add('Environment', stageConfig.environment);
    cdk.Tags.of(this).add('Service', 'eregs-waf');
  }

  // Helper method to associate WAF with API Gateway
  public associateWithApiGateway(apiGateway: cdk.aws_apigateway.RestApi): void {
    new wafv2.CfnWebACLAssociation(this, 'ApiGatewayWAFAssociation', {
      resourceArn: `arn:aws:apigateway:${cdk.Stack.of(this).region}::/restapis/${apiGateway.restApiId}/stages/${apiGateway.deploymentStage.stageName}`,
      webAclArn: this.webAcl.attrArn
    });
  }
}


// import * as cdk from 'aws-cdk-lib';
// import { aws_wafv2 as wafv2 } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';

// export class WafConstruct extends Construct {
//   public readonly webAcl: wafv2.CfnWebACL;

//   constructor(scope: Construct, id: string, stageConfig: StageConfig) {
//     super(scope, id);

//     this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
//       defaultAction: { allow: {} },
//       scope: 'REGIONAL',
//       visibilityConfig: {
//         cloudWatchMetricsEnabled: true,
//         metricName: stageConfig.getResourceName('api-metrics'),
//         sampledRequestsEnabled: true,
//       },
//       rules: [
//         {
//           name: stageConfig.getResourceName('allow-usa-territories'),
//           priority: 0,
//           statement: {
//             geoMatchStatement: {
//               countryCodes: ['US', 'GU', 'PR', 'VI', 'MP', 'AS', 'UM'],
//             },
//           },
//           action: { allow: {} },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: stageConfig.getResourceName('usa-territories-metric'),
//             sampledRequestsEnabled: true,
//           },
//         },
//       ],
//     });
//   }
// }