import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_rds as rds,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface DatabaseConstructProps {
    vpc: ec2.IVpc;
    dbPassword: string;
    securityGroup: ec2.SecurityGroup;
    vpcSubnets: ec2.SubnetSelection;  // Using CDK's type
  }
export class DatabaseConstruct extends Construct {
  public readonly dbCluster: rds.DatabaseCluster;  // Changed from cluster to dbCluster

  constructor(scope: Construct, id: string, props: DatabaseConstructProps) {
    super(scope, id);

    const parameterGroup = new rds.ParameterGroup(this, 'DBParameterGroup', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_2,
      }),
      parameters: {
        'rds.force_ssl': '1',
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
        'statement_timeout': '20000',
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

    // Log subnet configuration
    const subnetIds = props.vpcSubnets.subnets?.map(subnet => subnet.subnetId) || [];
    console.log('Database Subnet Configuration:', {
      subnetCount: subnetIds.length,
      subnetIds,
    });

    this.dbCluster = new rds.DatabaseCluster(this, 'Database', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_2,
      }),
      credentials: rds.Credentials.fromPassword(
        'eregsuser',
        cdk.SecretValue.unsafePlainText(props.dbPassword)
      ),
      instances: 1,
      instanceProps: {
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
        vpc: props.vpc,
        vpcSubnets: props.vpcSubnets,
        securityGroups: [props.securityGroup],
        parameterGroup,
      },
      defaultDatabaseName: 'eregs',
      storageEncrypted: true,
      backup: {
        retention: cdk.Duration.days(7),
      },
    });
  }
}
// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_rds as rds,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';

// interface DatabaseConstructProps {
//   vpc: ec2.IVpc;
//   dbPassword: string;
//   securityGroup: ec2.SecurityGroup;
// }

// export class DatabaseConstruct extends Construct {
//   public readonly cluster: rds.DatabaseCluster;

//   constructor(scope: Construct, id: string, props: DatabaseConstructProps) {
//     super(scope, id);

//     const parameterGroup = new rds.ParameterGroup(this, 'DBParameterGroup', {
//       engine: rds.DatabaseClusterEngine.auroraPostgres({
//         version: rds.AuroraPostgresEngineVersion.VER_15_2,
//       }),
//       parameters: {
//         'rds.force_ssl': '1',
//         'shared_preload_libraries': 'auto_explain,pg_stat_statements,pg_hint_plan,pgaudit',
//         'log_statement': 'ddl',
//         'log_connections': '1',
//         'log_disconnections': '1',
//         'log_lock_waits': '1',
//         'log_min_duration_statement': '5000',
//         'auto_explain.log_min_duration': '5000',
//         'auto_explain.log_verbose': '1',
//         'log_rotation_age': '1440',
//         'log_rotation_size': '102400',
//         'rds.log_retention_period': '10080',
//         'random_page_cost': '1',
//         'track_activity_query_size': '16384',
//         'idle_in_transaction_session_timeout': '7200000',
//         'statement_timeout': '20000',
//         'search_path': '"$user",public',
//         'log_hostname': '1',
//         'pgaudit.role': 'rds_pgaudit',
//         'pgaudit.log': 'ALL',
//         'pgaudit.log_level': 'LOG',
//         'pgaudit.log_parameter': '1',
//         'pgaudit.log_statement_once': '0',
//         'pgaudit.log_catalog': '1',
//       },
//     });

//     this.cluster = new rds.DatabaseCluster(this, 'Database', {
//       engine: rds.DatabaseClusterEngine.auroraPostgres({
//         version: rds.AuroraPostgresEngineVersion.VER_15_2,
//       }),
//       credentials: rds.Credentials.fromPassword(
//         'eregsuser',
//         cdk.SecretValue.unsafePlainText(props.dbPassword)
//       ),
//       instanceProps: {
//         instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
//         vpc: props.vpc,
//         securityGroups: [props.securityGroup],
//         parameterGroup,
//         vpcSubnets: {
//           subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
//         },
//       },
//       defaultDatabaseName: 'eregs',
//       storageEncrypted: true,
//       backup: {
//         retention: cdk.Duration.days(7),
//       },
//     });
//   }
// }