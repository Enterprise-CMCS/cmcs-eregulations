// lib/stacks/vpc-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';

export class VpcStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;  // Make vpc public

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create the VPC
    this.vpc = new ec2.Vpc(this, 'EregsVpc', {
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      maxAzs: 2, // Use 2 Availability Zones

      // Define subnet configuration
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
      ],

      // Enable DNS hostnames and DNS support
      enableDnsHostnames: true,
      enableDnsSupport: true,
    });

    // Store parameters with unique names for prod
    new ssm.StringParameter(this, 'VpcId', {
      parameterName: '/account_vars/vpc/prod/id',
      stringValue: this.vpc.vpcId,
      description: 'Production VPC ID',
      tier: ssm.ParameterTier.STANDARD,
    });

    // Store Private Subnet IDs with overwrite enabled
    const privateSubnets = this.vpc.selectSubnets({
      subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
    }).subnets;

    // Store first private subnet ID
    new ssm.StringParameter(this, 'PrivateSubnet1a', {
      parameterName: '/account_vars/vpc/prod/subnets/private/1a/id',
      stringValue: privateSubnets[0].subnetId,
      description: 'Production Private Subnet 1a',
    });

    // Store second private subnet ID
    new ssm.StringParameter(this, 'PrivateSubnet1b', {
      parameterName: '/account_vars/vpc/prod/subnets/private/1b/id',
      stringValue: privateSubnets[1].subnetId,
      description: 'Production Private Subnet 1b',
    });

    // Output the VPC and subnet IDs for reference
    new cdk.CfnOutput(this, 'VpcIdOutput', {
      value: this.vpc.vpcId,
      description: 'VPC ID',
    });

    new cdk.CfnOutput(this, 'PrivateSubnet1aOutput', {
      value: privateSubnets[0].subnetId,
      description: 'Private Subnet 1a ID',
    });
  }
}