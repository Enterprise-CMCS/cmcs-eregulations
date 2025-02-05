import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_rds as rds,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import { DatabaseConstruct } from '../constructs/database-construct';

interface DatabaseStackProps extends cdk.StackProps {
  environmentConfig: {
    vpcId: string;
    subnetIds: string[];
  };
}

/**
 * Database Stack that creates an Aurora PostgreSQL cluster
 * Uses environment-specific configuration and integrates with existing VPC
 */
export class DatabaseStack extends cdk.Stack {
  public readonly databaseConstruct: DatabaseConstruct;

  constructor(scope: Construct, id: string, props: DatabaseStackProps, stageConfig: StageConfig) {
    super(scope, id, props);

    // ================================
    // VPC CONFIGURATION
    // ================================
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId,
    });

    // Create subnet selection from provided subnet IDs
    const selectedSubnets: ec2.SubnetSelection = {
      subnets: props.environmentConfig.subnetIds.map(
        (subnetId, index) => ec2.Subnet.fromSubnetId(
          this,
          `PrivateSubnet${index + 1}`,
          subnetId
        )
      ),
    };

    // ================================
    // DATABASE CONSTRUCT
    // ================================
    this.databaseConstruct = new DatabaseConstruct(this, 'Database', {
      vpc,
      selectedSubnets,
      stageConfig,
    });

    // ================================
    // STACK OUTPUTS
    // ================================
    const outputs: Record<string, cdk.CfnOutputProps> = {
      DatabaseClusterEndpoint: {
        value: this.databaseConstruct.cluster.clusterEndpoint.hostname,
        description: 'Database cluster endpoint',
        exportName: stageConfig.getResourceName('db-cluster-endpoint'),
      },
      DatabaseSecurityGroupId: {
        value: this.databaseConstruct.dbSecurityGroup.securityGroupId,
        description: 'Database security group ID',
        exportName: stageConfig.getResourceName('db-security-group-id'),
      },
      DatabaseClusterArn: {
        value: this.databaseConstruct.cluster.clusterArn,
        description: 'Database cluster ARN',
        exportName: stageConfig.getResourceName('db-cluster-arn'),
      },
      DatabaseName: {
        value: 'eregs',
        description: 'Database name',
        exportName: stageConfig.getResourceName('db-name'),
      },
    };

    // Add special exports for dev environment
    if (stageConfig.environment === 'dev') {
      outputs.DevDatabaseEndpoint = {
        value: this.databaseConstruct.cluster.clusterEndpoint.hostname,
        description: 'Dev Database endpoint for ephemeral environments',
        exportName: `${StageConfig.projectName}-dev-db-endpoint`
      };

      outputs.DevDatabaseSecurityGroup = {
        value: this.databaseConstruct.dbSecurityGroup.securityGroupId,
        description: 'Dev Database security group ID for ephemeral environments',
        exportName: `${StageConfig.projectName}-dev-db-security-group`
      };
    }

    // Create all outputs
    Object.entries(outputs).forEach(([name, config]) => {
      new cdk.CfnOutput(this, name, config);
    });
  }
}

