import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

export interface DatabaseConstructProps {
  readonly vpc: ec2.IVpc;
  readonly selectedSubnets: ec2.SubnetSelection;
  readonly stageConfig: StageConfig;
}

export class DatabaseConstruct extends Construct {
  public readonly dbSecurityGroup: ec2.SecurityGroup;
  public readonly cluster: rds.DatabaseCluster;

  constructor(scope: Construct, id: string, props: DatabaseConstructProps) {
    super(scope, id);

    const { vpc, selectedSubnets, stageConfig } = props;

    // Retrieve DB credentials from Secrets Manager
    const dbSecret = secretsmanager.Secret.fromSecretNameV2(
      this,
      'DbSecret',
      '/eregulations/db/credentials'
    );

    // Create DB security group
    this.dbSecurityGroup = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
      vpc,
      description: `Database Security Group for ${stageConfig.stageName}`,
      allowAllOutbound: false,
      securityGroupName: stageConfig.getResourceName('db-security-group'),
    });

    // Import serverless security group and allow ingress
    const envServerlessSG = ec2.SecurityGroup.fromSecurityGroupId(
      this,
      'ServerlessSG',
      cdk.Fn.importValue(stageConfig.getResourceName('serverless-security-group'))
    );
    this.dbSecurityGroup.addIngressRule(
      envServerlessSG,
      ec2.Port.tcp(5432),
      `Allow PostgreSQL access from ${stageConfig.environment} Lambda functions`
    );

    // Define cluster parameter group
    const clusterParameterGroup = new rds.ParameterGroup(this, 'DBClusterParameterGroup', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_8,
      }),
      description: `Parameter group for ${stageConfig.stageName}`,
      parameters: {
        'rds.force_ssl': '1',
        'statement_timeout': '10000',
      },
    });

    // Define instance parameter group
    const instanceParameterGroup = new rds.ParameterGroup(this, 'DBInstanceParameterGroup', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_8,
      }),
      description: `Instance parameter group for ${stageConfig.stageName}`,
      parameters: {
        'shared_preload_libraries': 'auto_explain,pg_stat_statements,pg_hint_plan,pgaudit',
        'log_statement': 'ddl',
        'log_connections': '1',
        'log_disconnections': '1',
        'log_lock_waits': '1',
        'log_min_duration_statement': '5000',
        'auto_explain.log_min_duration': '5000',
        'auto_explain.log_verbose': '1',
        'log_rotation_age': '1440',
        'log_rotation_size': '102400',
        'rds.log_retention_period': '10080',
        'random_page_cost': '1',
        'track_activity_query_size': '16384',
        'idle_in_transaction_session_timeout': '7200000',
        'statement_timeout': '10000',
        'search_path': '"$user",public',
        'log_hostname': '1',
        'pgaudit.role': 'rds_pgaudit',
        'pgaudit.log': 'ALL',
        'pgaudit.log_level': 'LOG',
        'pgaudit.log_parameter': '1',
        'pgaudit.log_statement_once': '0',
        'pgaudit.log_catalog': '1',
      },
    });

    // Define the writer instance
    const writer = rds.ClusterInstance.provisioned('Instance', {
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
      parameterGroup: instanceParameterGroup,
      enablePerformanceInsights: true,
    });

    // Create the database cluster
    this.cluster = new rds.DatabaseCluster(this, 'Database', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_8,
      }),
      vpc,
      vpcSubnets: selectedSubnets,
      writer,
      securityGroups: [this.dbSecurityGroup],
      credentials: rds.Credentials.fromSecret(dbSecret),
      parameterGroup: clusterParameterGroup,
      defaultDatabaseName: 'eregs',
      storageEncrypted: true,
      backup: {
        retention: cdk.Duration.days(7),
      },
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      cloudwatchLogsExports: ['postgresql'],
    });

    // Create CloudFormation outputs
    if (stageConfig.environment === 'dev') {
      new cdk.CfnOutput(this, 'DevDatabaseEndpoint', {
        value: this.cluster.clusterEndpoint.hostname,
        description: 'Dev Database endpoint for ephemeral environments',
        exportName: `${StageConfig.projectName}-dev-db-endpoint`,
      });
      new cdk.CfnOutput(this, 'DevDatabaseSecurityGroup', {
        value: this.dbSecurityGroup.securityGroupId,
        description: 'Dev Database security group ID for ephemeral environments',
        exportName: `${StageConfig.projectName}-dev-db-security-group`,
      });
    }
    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: this.cluster.clusterEndpoint.hostname,
      exportName: stageConfig.getResourceName('db-endpoint'),
    });
    new cdk.CfnOutput(this, 'DatabaseSecurityGroup', {
      value: this.dbSecurityGroup.securityGroupId,
      exportName: stageConfig.getResourceName('db-security-group'),
    });
  }
}
