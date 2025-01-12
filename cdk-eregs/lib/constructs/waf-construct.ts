import * as cdk from 'aws-cdk-lib';
import {
  aws_wafv2 as wafv2,
  aws_logs as logs,
  aws_apigateway as apigw,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';

/**
 * StageConfig is a placeholder interface/class. 
 * Adapt it to fit your own project’s configuration needs.
 *
 * Example:
 *   export interface StageConfig {
 *     environment: string;
 *     getResourceName(baseName: string): string;
 *   }
 */
import { StageConfig } from '../../config/stage-config';

export class WafConstruct extends Construct {
  /** Publicly available WAFv2 Web ACL object */
  public readonly webAcl: wafv2.CfnWebACL;

  /** Reference to the created CloudWatch Log Group */
  private readonly logGroup: logs.LogGroup;

  constructor(scope: Construct, id: string, stageConfig: StageConfig) {
    super(scope, id);

    // -------------------------------------------------------
    // 1) CREATE THE LOG GROUP
    // -------------------------------------------------------
    this.logGroup = new logs.LogGroup(this, 'WafLogGroup', {
      logGroupName: stageConfig.getResourceName('waf-logs'),
      // 30 days retention; adjust for your compliance or cost needs
      retention: logs.RetentionDays.ONE_MONTH,
      // Destroy log group when stack is removed; 
      // if you need logs for forensic/historical reasons, switch to RETAIN
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // -------------------------------------------------------
    // 2) CREATE THE WAFv2 WEB ACL
    // -------------------------------------------------------
    this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
      // Visible name in the WAF console
      name: stageConfig.getResourceName('APIGateway-eregs-allow-usa-plus-territories'),
      // Could also be set to { block: {} } for a default deny strategy
      defaultAction: { allow: {} },
      // 'REGIONAL' for API Gateway, 'CLOUDFRONT' for distributions, etc.
      scope: 'REGIONAL',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: stageConfig.getResourceName('api-metrics'),
        sampledRequestsEnabled: true,
      },
      rules: [
        // ---------- GeoMatch Example ----------
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
        // ---------- Rate Limit Example ----------
        {
          name: stageConfig.getResourceName('rate-limit'),
          priority: 1,
          statement: {
            rateBasedStatement: {
              limit: 2000, // requests per 5-minute period
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
        // ---------- AWS Managed Rule Sets ----------
        {
          name: 'AWSManagedRulesCommonRuleSet',
          priority: 2,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesCommonRuleSet',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'AWSManagedRulesCommonRuleSetMetric',
            sampledRequestsEnabled: true,
          },
        },
        {
          name: 'AWSManagedRulesKnownBadInputsRuleSet',
          priority: 3,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesKnownBadInputsRuleSet',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'AWSManagedRulesKnownBadInputsRuleSetMetric',
            sampledRequestsEnabled: true,
          },
        },
      ],
    });

    // Make sure the Web ACL depends on the log group if needed for naming
    // (Not strictly necessary if just referencing ARNs, but good practice)
    this.webAcl.node.addDependency(this.logGroup);

    // -------------------------------------------------------
    // 3) FORMAT A CLEAN ARN FOR WAF LOGGING
    // -------------------------------------------------------
    // WAF requires a colon between "log-group" and the log group name, 
    // so we ensure no wildcards or slashes.
    const stack = cdk.Stack.of(this);
    const logGroupArnForWAF = cdk.Arn.format(
      {
        service: 'logs',
        resource: 'log-group',
        resourceName: this.logGroup.logGroupName,
        arnFormat: cdk.ArnFormat.COLON_RESOURCE_NAME,
      },
      stack,
    );

    // -------------------------------------------------------
    // 4) CREATE THE WAF LOGGING CONFIG
    // -------------------------------------------------------
    const loggingConfig = new wafv2.CfnLoggingConfiguration(this, 'WafLogging', {
      // Must use the correct colon-based ARN (no wildcards)
      logDestinationConfigs: [logGroupArnForWAF],
      resourceArn: this.webAcl.attrArn, // Link to the WAF ACL
    });

    // Ensure logging setup depends on both the log group & WAF
    loggingConfig.node.addDependency(this.logGroup);
    loggingConfig.node.addDependency(this.webAcl);

    // -------------------------------------------------------
    // 5) TAGGING (OPTIONAL BUT RECOMMENDED)
    // -------------------------------------------------------
    // Apply consistent tagging to help track environment, usage, cost, etc.
    cdk.Tags.of(this).add('Name', `eregs-waf-${stageConfig.environment}`);
    cdk.Tags.of(this).add('Environment', stageConfig.environment);
    cdk.Tags.of(this).add('Service', 'eregs-waf');
  }

  /**
   * Call this to associate your WAF with an API Gateway deployment.
   * e.g. usage: wafConstruct.associateWithApiGateway(myRestApi);
   */
  public associateWithApiGateway(apiGateway: apigw.RestApi): void {
    new wafv2.CfnWebACLAssociation(this, 'ApiGatewayWAFAssociation', {
      // REST API stage ARN format for WAF (REGIONAL)
      resourceArn: `arn:aws:apigateway:${cdk.Stack.of(this).region}::/restapis/${apiGateway.restApiId}/stages/${apiGateway.deploymentStage.stageName}`,
      webAclArn: this.webAcl.attrArn,
    });
  }

  /**
   * If you need the raw ARN of the log group for other operations,
   * you can retrieve it here. Note that it's the wildcard version (with :*),
   * so be cautious if you use it for a WAF destination. 
   */
  public getLogGroupArn(): string {
    return this.logGroup.logGroupArn;
  }
}

// import * as cdk from 'aws-cdk-lib';
// import { aws_wafv2 as wafv2, aws_logs as logs } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';

// export class WafConstruct extends Construct {
//   public readonly webAcl: wafv2.CfnWebACL;

//   constructor(scope: Construct, id: string, stageConfig: StageConfig) {
//     super(scope, id);

//     // Create WAF ACL matching serverless configuration
//     this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
//       name: stageConfig.getResourceName(`APIGateway-eregs-allow-usa-plus-territories`),
//       defaultAction: { allow: {} },
//       scope: 'REGIONAL',
//       visibilityConfig: {
//         cloudWatchMetricsEnabled: true,
//         metricName: stageConfig.getResourceName('api-metrics'),
//         sampledRequestsEnabled: true,
//       },
//       rules: [
//         // Geo restriction rule exactly matching serverless.yml
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
//         // Rate limiting rule
//         {
//           name: stageConfig.getResourceName('rate-limit'),
//           priority: 1,
//           statement: {
//             rateBasedStatement: {
//               limit: 2000,
//               aggregateKeyType: 'IP',
//             },
//           },
//           action: { block: {} },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: stageConfig.getResourceName('rate-limit-metric'),
//             sampledRequestsEnabled: true,
//           },
//         },
//         // AWS Managed Rule Sets
//         {
//           name: 'AWSManagedRulesCommonRuleSet',
//           priority: 2,
//           overrideAction: { none: {} },
//           statement: {
//             managedRuleGroupStatement: {
//               vendorName: 'AWS',
//               name: 'AWSManagedRulesCommonRuleSet'
//             }
//           },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: 'AWSManagedRulesCommonRuleSetMetric',
//             sampledRequestsEnabled: true
//           }
//         },
//         {
//           name: 'AWSManagedRulesKnownBadInputsRuleSet',
//           priority: 3,
//           overrideAction: { none: {} },
//           statement: {
//             managedRuleGroupStatement: {
//               vendorName: 'AWS',
//               name: 'AWSManagedRulesKnownBadInputsRuleSet'
//             }
//           },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: 'AWSManagedRulesKnownBadInputsRuleSetMetric',
//             sampledRequestsEnabled: true
//           }
//         }
//       ]
//     });

//     // Create log group for WAF logs
//     const logGroup = new logs.LogGroup(this, 'WafLogGroup', {
//       logGroupName: stageConfig.getResourceName('waf-logs'),
//       retention: logs.RetentionDays.ONE_MONTH,
//       removalPolicy: cdk.RemovalPolicy.DESTROY,
//     });

//     // Configure WAF logging
//     const loggingConfig = new wafv2.CfnLoggingConfiguration(this, 'WafLogging', {
//       logDestinationConfigs: [logGroup.logGroupArn],
//       resourceArn: this.webAcl.attrArn
//     });

//     // Add tags
//     cdk.Tags.of(this).add('Name', `eregs-waf-${stageConfig.environment}`);
//     cdk.Tags.of(this).add('Environment', stageConfig.environment);
//     cdk.Tags.of(this).add('Service', 'eregs-waf');
//   }

//   // Helper method to associate WAF with API Gateway
//   public associateWithApiGateway(apiGateway: cdk.aws_apigateway.RestApi): void {
//     new wafv2.CfnWebACLAssociation(this, 'ApiGatewayWAFAssociation', {
//       resourceArn: `arn:aws:apigateway:${cdk.Stack.of(this).region}::/restapis/${apiGateway.restApiId}/stages/${apiGateway.deploymentStage.stageName}`,
//       webAclArn: this.webAcl.attrArn
//     });
//   }
// }


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