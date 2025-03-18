import * as cdk from 'aws-cdk-lib';
import {
  aws_wafv2 as wafv2,
  aws_logs as logs,
  aws_apigateway as apigw,
  aws_iam as iam,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

export class WafConstruct extends Construct {
  /** Publicly available WAFv2 Web ACL object */
  public readonly webAcl: wafv2.CfnWebACL;

  /** Reference to the created CloudWatch Log Group */
  private readonly logGroup: logs.LogGroup;

  constructor(scope: Construct, id: string, stageConfig: StageConfig) {
    super(scope, id);

    // Create the log group with required prefix
    this.logGroup = new logs.LogGroup(this, 'WafLogGroup', {
      logGroupName: `aws-waf-logs-${stageConfig.getResourceName('waf')}`,
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Add a resource policy to allow WAF to write logs
    this.logGroup.addToResourcePolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        principals: [new iam.ServicePrincipal('waf.amazonaws.com')],
        actions: ['logs:CreateLogStream', 'logs:PutLogEvents'],
        resources: [`${this.logGroup.logGroupArn}:*`],
      }),
    );

    // Create the WAFv2 Web ACL
    this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
      name: stageConfig.getResourceName('APIGateway-eregs-allow-usa-plus-territories'),
      defaultAction: { allow: {} },
      scope: 'REGIONAL',
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: stageConfig.getResourceName('api-metrics'),
        sampledRequestsEnabled: true,
      },
      rules: [
        // GeoMatch Rule
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
        // Rate Limit Rule
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

    // Make sure WAF depends on log group
    this.webAcl.node.addDependency(this.logGroup);

    // Format a clean ARN for WAF logging
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

    // Create the WAF logging config
    const loggingConfig = new wafv2.CfnLoggingConfiguration(this, 'WafLogging', {
      logDestinationConfigs: [logGroupArnForWAF],
      resourceArn: this.webAcl.attrArn,
    });

    // Add explicit dependencies
    loggingConfig.node.addDependency(this.logGroup);
    loggingConfig.node.addDependency(this.webAcl);

    // Add resource tags
    cdk.Tags.of(this).add('Name', `eregs-waf-${stageConfig.environment}`);
    cdk.Tags.of(this).add('Environment', stageConfig.environment);
    cdk.Tags.of(this).add('Service', 'eregs-waf');
  }

  /**
   * Associate this WAF with an API Gateway deployment.
   * @param apiGateway The API Gateway to associate with the WAF
   */
  public associateWithApiGateway(apiGateway: apigw.RestApi): void {
    new wafv2.CfnWebACLAssociation(this, 'ApiGatewayWAFAssociation', {
      resourceArn: `arn:aws:apigateway:${cdk.Stack.of(this).region}::/restapis/${apiGateway.restApiId}/stages/${apiGateway.deploymentStage.stageName}`,
      webAclArn: this.webAcl.attrArn,  // Using attrArn from webAcl
    });
  }

  /**
   * Get the ARN of the Web ACL
   * @returns The ARN of the Web ACL
   */
  public getWebAclArn(): string {
    return this.webAcl.attrArn;
  }

  /**
   * Get the raw ARN of the log group
   * Note: this returns the wildcard version with :*
   */
  public getLogGroupArn(): string {
    return this.logGroup.logGroupArn;
  }
}

// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_wafv2 as wafv2,
//   aws_logs as logs,
//   aws_apigateway as apigw,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';

// export class WafConstruct extends Construct {
//   /** Publicly available WAFv2 Web ACL object */
//   public readonly webAcl: wafv2.CfnWebACL;

//   /** Reference to the created CloudWatch Log Group */
//   private readonly logGroup: logs.LogGroup;

//   constructor(scope: Construct, id: string, stageConfig: StageConfig) {
//     super(scope, id);

//     // -------------------------------------------------------
//     // 1) CREATE THE LOG GROUP WITH REQUIRED PREFIX
//     // -------------------------------------------------------
//     this.logGroup = new logs.LogGroup(this, 'WafLogGroup', {
//       // Use required 'aws-waf-logs-' prefix for WAF logging
//       logGroupName: `aws-waf-logs-${stageConfig.getResourceName('waf')}`,
//       retention: logs.RetentionDays.ONE_MONTH,
//       removalPolicy: cdk.RemovalPolicy.DESTROY,
//     });

//     // -------------------------------------------------------
//     // 2) CREATE THE WAFv2 WEB ACL
//     // -------------------------------------------------------
//     this.webAcl = new wafv2.CfnWebACL(this, 'APIGatewayWAF', {
//       name: stageConfig.getResourceName('APIGateway-eregs-allow-usa-plus-territories'),
//       defaultAction: { allow: {} },
//       scope: 'REGIONAL',
//       visibilityConfig: {
//         cloudWatchMetricsEnabled: true,
//         metricName: stageConfig.getResourceName('api-metrics'),
//         sampledRequestsEnabled: true,
//       },
//       rules: [
//         // ---------- GeoMatch Rule ----------
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
//         // ---------- Rate Limit Rule ----------
//         {
//           name: stageConfig.getResourceName('rate-limit'),
//           priority: 1,
//           statement: {
//             rateBasedStatement: {
//               limit: 2000,  // requests per 5-minute period
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
//         // ---------- AWS Managed Rule Sets ----------
//         {
//           name: 'AWSManagedRulesCommonRuleSet',
//           priority: 2,
//           overrideAction: { none: {} },
//           statement: {
//             managedRuleGroupStatement: {
//               vendorName: 'AWS',
//               name: 'AWSManagedRulesCommonRuleSet',
//             },
//           },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: 'AWSManagedRulesCommonRuleSetMetric',
//             sampledRequestsEnabled: true,
//           },
//         },
//         {
//           name: 'AWSManagedRulesKnownBadInputsRuleSet',
//           priority: 3,
//           overrideAction: { none: {} },
//           statement: {
//             managedRuleGroupStatement: {
//               vendorName: 'AWS',
//               name: 'AWSManagedRulesKnownBadInputsRuleSet',
//             },
//           },
//           visibilityConfig: {
//             cloudWatchMetricsEnabled: true,
//             metricName: 'AWSManagedRulesKnownBadInputsRuleSetMetric',
//             sampledRequestsEnabled: true,
//           },
//         },
//       ],
//     });

//     // Make sure WAF depends on log group
//     this.webAcl.node.addDependency(this.logGroup);

//     // -------------------------------------------------------
//     // 3) FORMAT A CLEAN ARN FOR WAF LOGGING
//     // -------------------------------------------------------
//     const stack = cdk.Stack.of(this);
//     const logGroupArnForWAF = cdk.Arn.format(
//       {
//         service: 'logs',
//         resource: 'log-group',
//         resourceName: this.logGroup.logGroupName,
//         arnFormat: cdk.ArnFormat.COLON_RESOURCE_NAME,
//       },
//       stack,
//     );

//     // -------------------------------------------------------
//     // 4) CREATE THE WAF LOGGING CONFIG
//     // -------------------------------------------------------
//     const loggingConfig = new wafv2.CfnLoggingConfiguration(this, 'WafLogging', {
//       logDestinationConfigs: [logGroupArnForWAF],
//       resourceArn: this.webAcl.attrArn,
//     });

//     // Add explicit dependencies
//     loggingConfig.node.addDependency(this.logGroup);
//     loggingConfig.node.addDependency(this.webAcl);

//     // -------------------------------------------------------
//     // 5) ADD RESOURCE TAGS
//     // -------------------------------------------------------
//     cdk.Tags.of(this).add('Name', `eregs-waf-${stageConfig.environment}`);
//     cdk.Tags.of(this).add('Environment', stageConfig.environment);
//     cdk.Tags.of(this).add('Service', 'eregs-waf');
//   }

//   /**
//    * Associate this WAF with an API Gateway deployment.
//    * @param apiGateway The API Gateway to associate with the WAF
//    */
//   public associateWithApiGateway(apiGateway: apigw.RestApi): void {
//     new wafv2.CfnWebACLAssociation(this, 'ApiGatewayWAFAssociation', {
//       resourceArn: `arn:aws:apigateway:${cdk.Stack.of(this).region}::/restapis/${apiGateway.restApiId}/stages/${apiGateway.deploymentStage.stageName}`,
//       webAclArn: this.webAcl.attrArn,
//     });
//   }

//   /**
//    * Get the raw ARN of the log group
//    * Note: this returns the wildcard version with :*
//    */
//   public getLogGroupArn(): string {
//     return this.logGroup.logGroupArn;
//   }
// }
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
