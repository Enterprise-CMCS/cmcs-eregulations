import * as cdk from 'aws-cdk-lib';
import {
  aws_iam as iam,
  aws_logs as logs,
  aws_lambda as lambda,
  aws_events as events,
  aws_events_targets as targets,
  aws_ec2 as ec2,
  Tags,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StageConfig } from '../../config/stage-config';
import * as path from 'path';

interface LambdaConfig {
  timeout: number;
}

interface EnvironmentConfig {
  vpcId: string;
  httpUser: string;
  httpPassword: string;
  logLevel: string;
}

export interface FrParserStackProps extends cdk.StackProps {
  lambdaConfig: LambdaConfig;
  environmentConfig: EnvironmentConfig;
}

export class FrParserStack extends cdk.Stack {
  public readonly lambda: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: FrParserStackProps,
    stageConfig: StageConfig
  ) {
    super(scope, id, props);

    // Create VPC reference
    const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
      vpcId: props.environmentConfig.vpcId
    });

    // Create security group
    const securityGroup = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
      vpc,
      description: 'SecurityGroup for Serverless Functions',
      allowAllOutbound: true,
    });

    Tags.of(securityGroup).add('Name', 'ServerlessSecurityGroup');

    // Create Lambda infrastructure
    const { lambdaRole, logGroup } = this.createLambdaInfrastructure(stageConfig);

    // Get the site stack endpoint using stageConfig
    const siteEndpoint = cdk.Fn.importValue(`${stageConfig.getResourceName('site')}-ServiceEndpoint`);

    // Create Lambda function
    this.lambda = new lambda.DockerImageFunction(this, 'FrParserFunction', {
      functionName: stageConfig.getResourceName('fr-parser'),
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/parser/'), {
        file: 'fr-parser/Dockerfile',
      }),
      vpc,
      securityGroups: [securityGroup],
      timeout: cdk.Duration.seconds(props.lambdaConfig.timeout || 900),
      environment: {
        PARSER_ON_LAMBDA: 'true',
        EREGS_USERNAME: props.environmentConfig.httpUser,
        EREGS_PASSWORD: props.environmentConfig.httpPassword,
        EREGS_API_URL_V3: `${siteEndpoint}/v3/`,
        STAGE_ENV: stageConfig.environment,
        LOG_LEVEL: props.environmentConfig.logLevel,
      },
      role: lambdaRole,
    });

    // Create CloudWatch Event Rule
    const rule = new events.Rule(this, 'FrParserSchedule', {
      schedule: events.Schedule.expression('cron(0 2 * * ? *)'),
      enabled: true,
    });

    rule.addTarget(new targets.LambdaFunction(this.lambda));

    // Create stack outputs
    this.createStackOutputs(stageConfig);
  }

  private createLambdaInfrastructure(stageConfig: StageConfig) {
    const logGroup = new logs.LogGroup(this, 'FrParserLogGroup', {
      logGroupName: stageConfig.aws.lambda('fr-parser'),
      retention: logs.RetentionDays.INFINITE,
    });

    const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
      path: stageConfig.iamPath,
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
        this,
        'PermissionsBoundary',
        stageConfig.permissionsBoundaryArn
      ),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
      ],
      inlinePolicies: {
        LambdaPolicy: this.createLambdaPolicy(),
      },
    });

    return { lambdaRole, logGroup };
  }

  private createLambdaPolicy(): iam.PolicyDocument {
    return new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'logs:CreateLogGroup',
            'logs:CreateLogStream',
            'logs:PutLogEvents'
          ],
          resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
        }),
      ],
    });
  }

  private createStackOutputs(stageConfig: StageConfig) {
    // Output the Lambda function ARN
    new cdk.CfnOutput(this, 'FrParserLambdaFunctionQualifiedArn', {
      value: this.lambda.currentVersion.functionArn,
      description: 'Current Lambda function version',
      exportName: `sls-${stageConfig.getResourceName('fr-parser')}-FrParserLambdaFunctionQualifiedArn`,
    });
  }
}
// import * as cdk from 'aws-cdk-lib';
// import {
//   aws_iam as iam,
//   aws_logs as logs,
//   aws_lambda as lambda,
//   aws_events as events,
//   aws_events_targets as targets,
//   aws_ec2 as ec2,
//   aws_s3 as s3,
// } from 'aws-cdk-lib';
// import { Construct } from 'constructs';
// import { StageConfig } from '../../config/stage-config';
// import * as path from 'path';

// interface LambdaConfig {
//   memorySize: number;
//   timeout: number;
// }

// interface EnvironmentConfig {
//   vpcId: string;
//   parserOnLambda: boolean;
//   eregsUsername: string;
//   eregsPassword: string;
//   siteStackName: string;  // For cross-stack reference
// }

// export interface FrParserStackProps extends cdk.StackProps {
//   lambdaConfig: LambdaConfig;
//   environmentConfig: EnvironmentConfig;
// }

// export class FrParserStack extends cdk.Stack {
//   public readonly lambda: lambda.Function;
//   public readonly deploymentBucket: s3.Bucket;

//   constructor(
//     scope: Construct,
//     id: string,
//     props: FrParserStackProps,
//     stageConfig: StageConfig
//   ) {
//     super(scope, id, props);


//     // Create VPC reference
//     const vpc = ec2.Vpc.fromLookup(this, 'VPC', {
//       vpcId: props.environmentConfig.vpcId
//     });

//     // Create security group
//     const securityGroup = new ec2.SecurityGroup(this, 'ServerlessSecurityGroup', {
//       vpc,
//       description: 'SecurityGroup for Serverless Functions',
//       allowAllOutbound: true,
//     });

//     // securityGroup.addTag('Name', 'ServerlessSecurityGroup');

//     // Create Lambda infrastructure
//     const { lambdaRole, logGroup } = this.createLambdaInfrastructure(stageConfig);

//     // Create Lambda function
//     this.lambda = this.createFrParserLambdaFunction(
//       props.lambdaConfig,
//       props.environmentConfig,
//       lambdaRole,
//       vpc,
//       securityGroup,
//       stageConfig
//     );

//     // Create CloudWatch Event Rule
//     this.createScheduledTrigger();

//     // Create stack outputs
//     this.createStackOutputs(stageConfig);
//   }

//   private createFrParserLambdaFunction(
//     config: LambdaConfig,
//     envConfig: EnvironmentConfig,
//     role: iam.Role,
//     vpc: ec2.IVpc,
//     securityGroup: ec2.SecurityGroup,
//     stageConfig: StageConfig,
//   ): lambda.Function {
//     // Get the site stack endpoint from cross-stack reference
//     const siteEndpoint = cdk.Fn.importValue(`${envConfig.siteStackName}-ServiceEndpoint`);

//     return new lambda.DockerImageFunction(this, 'FrParserFunction', {
//       functionName: stageConfig.getResourceName('fr-parser'),
//       code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../../solution/'), {
//         file: '/parser/fr-parser/Dockerfile',
//       }),
//       vpc,
//       securityGroups: [securityGroup],
//       memorySize: config.memorySize,
//       timeout: cdk.Duration.seconds(config.timeout),
//       environment: {
//         PARSER_ON_LAMBDA: envConfig.parserOnLambda.toString(),
//         EREGS_USERNAME: envConfig.eregsUsername,
//         EREGS_PASSWORD: envConfig.eregsPassword,
//         EREGS_API_URL_V3: `${siteEndpoint}/v3/`,
//         STAGE_ENV: stageConfig.environment,
//       },
//       role,
//     });
//   }

//   private createScheduledTrigger() {
//     const rule = new events.Rule(this, 'FrParserSchedule', {
//       schedule: events.Schedule.expression('cron(0 2 * * ? *)'),
//       enabled: true,
//     });

//     rule.addTarget(new targets.LambdaFunction(this.lambda));
//   }

//   private createLambdaInfrastructure(stageConfig: StageConfig) {
//     const logGroup = new logs.LogGroup(this, 'FrParserLogGroup', {
//       logGroupName: stageConfig.aws.lambda('fr-parser'),
//       retention: logs.RetentionDays.INFINITE,
//     });

//     const lambdaRole = new iam.Role(this, 'LambdaFunctionRole', {
//       path: stageConfig.iamPath,
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'PermissionsBoundary',
//         stageConfig.permissionsBoundaryArn
//       ),
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
//       ],
//       inlinePolicies: {
//         LambdaPolicy: this.createLambdaPolicy(stageConfig),
//       },
//     });

//     return { lambdaRole, logGroup };
//   }

//   private createLambdaPolicy(stageConfig: StageConfig): iam.PolicyDocument {
//     return new iam.PolicyDocument({
//       statements: [
//         new iam.PolicyStatement({
//           effect: iam.Effect.ALLOW,
//           actions: [
//             'logs:CreateLogGroup',
//             'logs:CreateLogStream',
//             'logs:PutLogEvents'
//           ],
//           resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/*:*:*`],
//         }),
//         new iam.PolicyStatement({
//           effect: iam.Effect.ALLOW,
//           actions: [
//             's3:PutObject'
//           ],
//           resources: [
//             this.deploymentBucket.arnForObjects('*')
//           ],
//         }),
//       ],
//     });
//   }

//   private createStackOutputs(stageConfig: StageConfig) {
//     // Output the deployment bucket name
  
//     // Output the Lambda function ARN
//     new cdk.CfnOutput(this, 'FrParserLambdaFunctionQualifiedArn', {
//       value: this.lambda.currentVersion.functionArn,
//       description: 'Current Lambda function version',
//       exportName: `sls-${stageConfig.getResourceName('fr-parser')}-FrParserLambdaFunctionQualifiedArn`,
//     });
//   }
// }