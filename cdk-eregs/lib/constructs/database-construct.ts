import * as cdk from 'aws-cdk-lib';
import {
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';

/**
 * Properties required for the Database Construct
 * @interface DatabaseConstructProps
 */
interface DatabaseConstructProps {
  /** VPC where database resources will be deployed */
  vpc: ec2.IVpc;
  /** Selected subnets for database deployment */
  selectedSubnets: ec2.SubnetSelection;
  /** Stage configuration for environment-specific settings */
  stageConfig: StageConfig;
}

/**
 * Creates an Aurora PostgreSQL database with associated resources.
 * Handles security group access based on environment type:
 * - Regular environments (dev, val, prod) create and use their own security groups
 * - Dev environment exports values for ephemeral environment use
 * - Ephemeral environments use the dev security group for database access
 * @remarks
 * Database parameters match Serverless framework configuration exactly
 */
export class DatabaseConstruct extends Construct {
  /** Security group for the database instance */
  public readonly dbSecurityGroup: ec2.SecurityGroup;
  /** The Aurora database cluster */
  public readonly cluster: rds.DatabaseCluster;

  constructor(scope: Construct, id: string, props: DatabaseConstructProps) {
    super(scope, id);

    const { vpc, selectedSubnets, stageConfig } = props;

    // Get DB credentials from Secrets Manager
    const dbSecret = secretsmanager.Secret.fromSecretNameV2(
      this,
      'DbSecret',
      '/eregulations/db/credentials'
    );

    // Create database security group
    this.dbSecurityGroup = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
      vpc,
      description: `Database Security Group for ${stageConfig.stageName}`,
      allowAllOutbound: false,
      securityGroupName: stageConfig.getResourceName('db-security-group'),
    });

    // Import the appropriate serverless security group and allow access
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

    // Create cluster parameter group
    const clusterParameterGroup = new rds.ParameterGroup(this, 'DBClusterParameterGroup', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_8,
      }),
      description: `Parameter group for ${stageConfig.stageName}`,
      parameters: {
        'rds.force_ssl': '1',
        'statement_timeout': '10000'
      }
    });

    // Create instance parameter group
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
      }
    });

    // Create database cluster
    this.cluster = new rds.DatabaseCluster(this, 'Database', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_8,
      }),
      instanceProps: {
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
        vpc,
        vpcSubnets: selectedSubnets,
        securityGroups: [this.dbSecurityGroup],
        parameterGroup: instanceParameterGroup,
        enablePerformanceInsights: true,
      },
      credentials: rds.Credentials.fromSecret(dbSecret),
      instances: 1,
      parameterGroup: clusterParameterGroup,
      defaultDatabaseName: 'eregs',
      storageEncrypted: true,
      backup: {
        retention: cdk.Duration.days(7),
      },
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      cloudwatchLogsExports: ['postgresql'],
    });

    // Special exports for dev environment
    if (stageConfig.environment === 'dev') {
      new cdk.CfnOutput(this, 'DevDatabaseEndpoint', {
        value: this.cluster.clusterEndpoint.hostname,
        description: 'Dev Database endpoint for ephemeral environments',
        exportName: `${StageConfig.projectName}-dev-db-endpoint`
      });

      new cdk.CfnOutput(this, 'DevDatabaseSecurityGroup', {
        value: this.dbSecurityGroup.securityGroupId,
        description: 'Dev Database security group ID for ephemeral environments',
        exportName: `${StageConfig.projectName}-dev-db-security-group`
      });
    }

    // Regular exports
    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: this.cluster.clusterEndpoint.hostname,
      exportName: stageConfig.getResourceName('db-endpoint')
    });

    new cdk.CfnOutput(this, 'DatabaseSecurityGroup', {
      value: this.dbSecurityGroup.securityGroupId,
      exportName: stageConfig.getResourceName('db-security-group')
    });
  }
}
// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_ec2 as ec2,
//   aws_rds as rds,
//   aws_ssm as ssm,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';

// interface DatabaseStackProps extends cdk.StackProps {
//   environmentConfig: {
//     vpcId: string;
//     subnetIds: string[];
//   };
// }

// export class DatabaseStack extends cdk.Stack {
//   public readonly dbSecurityGroup: ec2.SecurityGroup;
//   public readonly serverlessSecurityGroup: ec2.SecurityGroup;

//   constructor(scope: Construct, id: string, props: DatabaseStackProps, stageConfig: StageConfig) {
//     super(scope, id, props);

//     // Get DB password from SSM
//     const dbPassword = ssm.StringParameter.valueForStringParameter(
//       this,
//       '/eregulations/db/password'
//     );

//     // VPC lookup
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId,
//     });

//     // Create subnet selection
//     const selectedSubnets: ec2.SubnetSelection = {
//       subnets: props.environmentConfig.subnetIds.map((subnetId, index) =>
//         ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
//       ),
//     };

//     // Create security groups
//     this.serverlessSecurityGroup = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Serverless Functions',
//       allowAllOutbound: true,
//     });

//     this.dbSecurityGroup = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Database',
//       allowAllOutbound: false,
//     });

//     // Allow database access from serverless security group
//     this.dbSecurityGroup.addIngressRule(
//       this.serverlessSecurityGroup,
//       ec2.Port.tcp(5432),
//       'Allow PostgreSQL access from Lambda functions',
//     );

//     // Create cluster parameter group
//     const clusterParameterGroup = new rds.ParameterGroup(this, 'DBClusterParameterGroup', {
//       engine: rds.DatabaseClusterEngine.auroraPostgres({
//         version: rds.AuroraPostgresEngineVersion.VER_15_2,
//       }),
//       parameters: {
//         'rds.force_ssl': '1',
//       },
//     });

//     // Create instance parameter group
//     const instanceParameterGroup = new rds.ParameterGroup(this, 'DBInstanceParameterGroup', {
//       engine: rds.DatabaseClusterEngine.auroraPostgres({
//         version: rds.AuroraPostgresEngineVersion.VER_15_2,
//       }),
//       parameters: {
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

//     // Create database cluster
//     const dbCluster = new rds.DatabaseCluster(this, 'Database', {
//       engine: rds.DatabaseClusterEngine.auroraPostgres({
//         version: rds.AuroraPostgresEngineVersion.VER_15_2,
//       }),
//       instanceProps: {
//         instanceType: ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE),
//         vpc,
//         vpcSubnets: selectedSubnets,
//         securityGroups: [this.dbSecurityGroup],
//         parameterGroup: instanceParameterGroup,
//         enablePerformanceInsights: true,
//       },
//       credentials: rds.Credentials.fromPassword(
//         'eregsuser',
//         cdk.SecretValue.unsafePlainText(dbPassword)
//       ),
//       instances: 1,
//       parameterGroup: clusterParameterGroup,
//       defaultDatabaseName: 'eregs',
//       storageEncrypted: true,
//       backup: {
//         retention: cdk.Duration.days(7),
//       },
//       removalPolicy: cdk.RemovalPolicy.RETAIN,
//       cloudwatchLogsExports: ['postgresql'],
//     });

//     // Export values needed by the application stack
//     new cdk.CfnOutput(this, 'DatabaseEndpoint', {
//       value: dbCluster.clusterEndpoint.hostname,
//       description: 'Database cluster endpoint',
//       exportName: stageConfig.getResourceName('db-endpoint'),
//     });

//     new cdk.CfnOutput(this, 'DatabaseSecurityGroup', {
//       value: this.dbSecurityGroup.securityGroupId,
//       description: 'Database security group ID',
//       exportName: stageConfig.getResourceName('db-security-group'),
//     });

//     new cdk.CfnOutput(this, 'ServerlessSecurityGroup', {
//       value: this.serverlessSecurityGroup.securityGroupId,
//       description: 'Serverless security group ID',
//       exportName: stageConfig.getResourceName('serverless-security-group'),
//     });

//     // Add tags
//     cdk.Tags.of(this).add('Environment', stageConfig.environment);
//     cdk.Tags.of(this).add('Service', 'eregs-database');
//   }
// }
