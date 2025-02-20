import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class ApiGatewayLoggingRole extends Construct {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Create the role that API Gateway will use for CloudWatch logging
    const role = new iam.Role(this, 'ApiGatewayCloudWatchRole', {
      assumedBy: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      description: 'Role used by API Gateway to push logs to CloudWatch',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          'service-role/AmazonAPIGatewayPushToCloudWatchLogs'
        ),
      ],
    });

    // Create a CfnAccount resource to update API Gateway account settings
    new cdk.aws_apigateway.CfnAccount(this, 'ApiGatewayAccount', {
      cloudWatchRoleArn: role.roleArn,
    });
  }
}