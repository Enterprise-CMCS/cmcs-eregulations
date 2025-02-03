import * as cdk from 'aws-cdk-lib';
import { aws_ec2 as ec2 } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import { DatabaseConstruct } from '../constructs/database-construct';

/**
 * Properties for the Database Stack
 * @interface DatabaseStackProps
 */
interface DatabaseStackProps extends cdk.StackProps {
  /** Environment configuration */
  environmentConfig: {
    /** VPC ID where database will be deployed */
    vpcId: string;
    /** Subnet IDs for database deployment */
    subnetIds: string[];
  };
}

/**
 * Stack that creates an Aurora PostgreSQL database using the DatabaseConstruct.
 * Handles security groups and database access for different environment types:
 * - Regular environments (dev, val, prod) use their own security groups
 * - Dev environment exports values for ephemeral environments
 * - Ephemeral environments use the dev database and security group
 * 
 * @remarks
 * The database configuration matches the Serverless framework exactly,
 * including all parameters and settings. Security groups are handled
 * differently to support ephemeral environments accessing dev database.
 */
export class DatabaseStack extends cdk.Stack {
  /** Security group for the database instance */
  public readonly dbSecurityGroup: ec2.SecurityGroup;

  constructor(scope: Construct, id: string, props: DatabaseStackProps, stageConfig: StageConfig) {
    super(scope, id, props);

    // VPC lookup
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId,
    });

    // Create subnet selection
    const selectedSubnets: ec2.SubnetSelection = {
      subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
        ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
      ),
    };

    // Create database construct
    const database = new DatabaseConstruct(this, 'Database', {
      vpc,
      selectedSubnets,
      stageConfig,
    });

    // Export security group for use in other stacks
    this.dbSecurityGroup = database.dbSecurityGroup;

    // Add standard tags
    const tags = {
      Environment: stageConfig.environment,
      Service: 'eregs-database',
      ManagedBy: 'CDK',
      ...stageConfig.getStackTags()
    };

    Object.entries(tags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });
  }
}