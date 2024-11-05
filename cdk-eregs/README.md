# Welcome to your CDK TypeScript project

<<<<<<< HEAD
Project Overview
The Redirect API stack is a Serverless application that leverages AWS services such as Lambda, API Gateway, CloudFormation, and IAM for creating, deploying, and managing a backend service. This setup is modular, allowing for easy customization, updates, and addition of new stacks through a StackFactory design.

Key Components of the Architecture
Lambda Function (redirectFunction):

Implements core backend functionality.
Integrated with API Gateway to handle HTTP requests.
Configurable for ephemeral and permanent environments by modifying memory, runtime, and timeout.
API Gateway:

Provides an HTTP interface to interact with the Lambda function.
Supports binary media types like multipart/form-data and application/pdf.
Logs API requests to CloudWatch for monitoring and debugging.
IAM Roles:

A role with restricted permissions, LambdaFunctionRole, grants only the required permissions to the Lambda function for security.
CloudFormation StackFactory:

Provides a reusable and modular way to create and manage multiple AWS stacks by defining configurations.
Enables easy setup for ephemeral environments like pull request previews.
Files Overview
1. redirect-api-stack.ts - Redirect API Stack
This file contains the main RedirectApiStack class, defining resources for the API Gateway, Lambda function, IAM roles, and CloudWatch log groups. Here’s a breakdown of its components:

LambdaConfig and ApiGatewayConfig interfaces define the structure for customizable configurations like memory size, timeout, handler, and API Gateway settings.
RedirectApiStackProps: Extends cdk.StackProps to include stage, appName, lambdaConfig, and optional apiConfig for flexibility.
Lambda Function Creation:
createLambdaInfrastructure creates IAM roles and log groups for Lambda.
createLambdaFunction initializes the Lambda function, setting its environment variables and memory settings.
API Gateway Integration:
createApiGateway sets up the API Gateway with defined binary media types and logging.
configureApiGateway links API Gateway and Lambda, managing permissions for invocation.
2. stack-factory.ts - Stack Factory
Defines a StackFactory class to create and configure stacks based on dynamic configurations.

Factory Design: This factory enables you to add new stacks by simply extending the stack configuration.
Configuration Mapping:
getStackProps dynamically maps configurations for different stack types, like redirect-api.
Supports additional configurations like data-pipeline or other stacks as the project grows.
3. stage-config.ts - Environment and Stage Configuration
The StageConfig class provides environment-specific settings, such as iamPath, permissionsBoundaryArn, and tags.
Ephemeral Environment Support: Optional ephemeralId for preview environments, used in stack naming to prevent resource conflicts.
Deployment and Configuration
1. Deployment with CDK CLI
To deploy the stack, navigate to the root directory of the project and run:

bash
Copy code
npx cdk deploy
This will:

Validate the environment.
Fetch necessary configurations from AWS SSM Parameter Store.
Deploy resources as per the specified environment.
2. Setting Up Ephemeral Environments
Ephemeral environments are useful for temporary deployments, like testing pull requests.

Ensure the StackFactory and StageConfig classes are configured to handle ephemeralId.
Set GITHUB_EVENT_NUMBER or DEPLOY_ENV environment variables to dynamically create ephemeral stack names.
Deploy the stack using the same cdk deploy command but with environment variables set for ephemeral use.
3. Using Serverless Framework
For managing serverless applications, the Serverless Framework config in serverless.yml allows easy deployment of Lambda functions and API Gateway.

yaml
Copy code
service: redirect-api

provider:
  name: aws
  runtime: python3.12
  ...
Modifying the Stack
To update or add features, follow these guidelines:

1. Modify Existing Resources
If you need to update the configuration of an existing resource (e.g., increasing Lambda memory):

Update RedirectApiStackProps or Lambda settings in redirect-api-stack.ts.
For example, increase memorySize or timeout in the LambdaConfig interface.
Redeploy with npx cdk deploy.
2. Adding a New Stack Type
To add a new stack, such as a data processing stack, follow these steps:

Create a New Stack Class:

Create a new file, e.g., data-pipeline-stack.ts.
Define a stack class, DataPipelineStack, extending cdk.Stack.
Define Configuration:

Extend StackConfig to include a new configuration type.

Map the new stack to StackFactory in stack-definitions.ts:

typescript
Copy code
export const StackType = {
  REDIRECT_API: 'redirect-api',
  DATA_PIPELINE: 'data-pipeline',
};
Update getStackConfigs:

Add configuration logic in getStackConfigs in stack-definitions.ts.
Return the necessary configurations based on environment and stack type.
3. Adding Permissions and Policies
Add permissions in redirect-api-stack.ts using addPermission or inlinePolicies in createLambdaInfrastructure if new AWS services are required.

4. API Gateway Customization
Modify the ApiGatewayConfig properties in redirect-api-stack.ts to customize binary media types, logging levels, or endpoint types.

Example: Adding a New Stack Configuration
Here’s an example of how to add a new configuration:

typescript
Copy code
// lib/config/stack-definitions.ts
export interface DataPipelineConfig extends BaseStackConfig {
  type: typeof StackType.DATA_PIPELINE;
  batchSize: number;
}

// In StackFactory getStackProps method:
case 'data-pipeline':
  return {
    ...baseProps,
    batchSize: stackConfig.batchSize,
  } as DataPipelineStackProps;
=======
This is a blank project for CDK development with TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
>>>>>>> main
