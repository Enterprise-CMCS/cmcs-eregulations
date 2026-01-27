import * as cdk from 'aws-cdk-lib';
import {
    aws_wafv2 as wafv2,
    aws_logs as logs,
    aws_apigateway as apigw,
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
                // GeoMatch Rule (Block non-USA and territories)
                {
                    name: stageConfig.getResourceName('block-non-usa-territories'),
                    priority: 0,
                    statement: {
                        notStatement: {
                            statement: {
                                geoMatchStatement: {
                                    countryCodes: ['US', 'GU', 'PR', 'VI', 'MP', 'AS', 'UM'],
                                },
                            },
                        },
                    },
                    action: { block: {} },
                    visibilityConfig: {
                        cloudWatchMetricsEnabled: true,
                        metricName: stageConfig.getResourceName('non-usa-territories-metric'),
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
        apiGateway.latestDeployment?.addToLogicalId(this.webAcl.attrArn);
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
