// // lib/stacks/maintenance-lambda-stack.ts
// import * as cdk from 'aws-cdk-lib';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as apigateway from 'aws-cdk-lib/aws-apigateway';
// import * as iam from 'aws-cdk-lib/aws-iam';
// import * as path from 'path';
// import { Construct } from 'constructs';
// import { EnvironmentConfigStack } from '../../config/environment-config';

// interface MaintenanceLambdaStackProps extends cdk.StackProps {
//   envStack: EnvironmentConfigStack;
// }

// export class MaintenanceLambdaStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props: MaintenanceLambdaStackProps) {
//     super(scope, id, props);

//     const { envStack } = props;
//     const { baseConfig, maintenanceConfig, iamConfig } = envStack;

//     // Create Lambda Role
//     const lambdaRole = new iam.Role(this, 'MaintenanceLambdaRole', {
//       assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
//       path: iamConfig.path,
//       managedPolicies: [
//         iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
//       ],
//       permissionsBoundary: iam.ManagedPolicy.fromManagedPolicyArn(
//         this,
//         'PermissionsBoundary',
//         `arn:aws:iam::${this.account}:policy${iamConfig.permissionsBoundaryPolicy}`
//       ),
//     });

//     // Create Maintenance Lambda
//     const maintenanceLambda = new lambda.Function(this, 'MaintenanceFunction', {
//       runtime: lambda.Runtime.PYTHON_3_9,
//       handler: 'maintenance.handler',
//       code: lambda.Code.fromAsset(path.join(__dirname, '../../../solution/backend/')),
//       functionName: `${baseConfig.stackPrefix}-maintenance`,
//       timeout: cdk.Duration.seconds(30),
//       memorySize: 128,
//       role: lambdaRole,
//       environment: {
//         STAGE: baseConfig.environment,
//         MAINTENANCE_WINDOW: maintenanceConfig.maintenanceWindow,
//         ALLOWED_IPS: JSON.stringify(maintenanceConfig.allowedIps),
//       },
//     });

//     // Create API Gateway
//     const api = new apigateway.RestApi(this, 'MaintenanceApi', {
//       restApiName: `${baseConfig.stackPrefix}-maintenance-api`,
//       deployOptions: {
//         stageName: baseConfig.environment,
//         tracingEnabled: true,
//         metricsEnabled: true,
//         loggingLevel: apigateway.MethodLoggingLevel.INFO,
//       },
//     });

//     // Add resource and method
//     const maintenance = api.root.addResource('maintenance');
//     maintenance.addMethod('GET', new apigateway.LambdaIntegration(maintenanceLambda));

//     // Add stack tags
//     Object.entries(baseConfig.tags).forEach(([key, value]) => {
//       cdk.Tags.of(this).add(key, value);
//     });