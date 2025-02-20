import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
  aws_ssm as ssm,
  aws_logs as logs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

export interface DatabaseConstructProps {
  readonly vpc: ec2.IVpc;
  readonly selectedSubnets: ec2.SubnetSelection;
  readonly stageConfig: StageConfig;
  readonly serverlessSecurityGroup: ec2.ISecurityGroup;
}
export class DatabaseConstruct extends Construct {
  public readonly dbSecurityGroup: ec2.SecurityGroup;
  public readonly cluster: rds.DatabaseCluster;

  constructor(scope: Construct, id: string, props: DatabaseConstructProps) {
    super(scope, id);

    const { vpc, selectedSubnets, stageConfig, serverlessSecurityGroup } = props;

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


    this.dbSecurityGroup.addIngressRule(
      serverlessSecurityGroup,
      ec2.Port.tcp(3306),
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



    // Create the database cluster
    this.cluster = new rds.DatabaseCluster(this, 'Database', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_8,
      }),
      vpc,
      vpcSubnets: selectedSubnets,
      serverlessV2MinCapacity: 0.5, // Minimum ACU (Aurora Capacity Units)
      serverlessV2MaxCapacity: 1, // Maximum ACU
      writer: rds.ClusterInstance.serverlessV2('Writer', {
        parameterGroup: instanceParameterGroup
      }),
      securityGroups: [this.dbSecurityGroup],
      credentials: rds.Credentials.fromSecret(dbSecret, 'eregsuser'),
      parameterGroup: clusterParameterGroup,
      defaultDatabaseName: 'eregs',
      storageEncrypted: true,
      port: 3306,
      backup: {
        retention: cdk.Duration.days(7),
      },
      cloudwatchLogsExports: ['postgresql'],
      cloudwatchLogsRetention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Create CloudFormation outputs
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
