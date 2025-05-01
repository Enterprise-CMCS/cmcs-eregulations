# CDK Infrastructure for eRegs

## Overview
This repository contains the AWS CDK (Cloud Development Kit) infrastructure code for the eRegs project. It is designed to manage and deploy various AWS resources, including Lambda functions, API Gateways, S3 buckets, and more, with environment-aware configurations and support for ephemeral environments.

## Key Features
- **Environment-Aware Deployments**: Automatically configures resources based on the target environment (e.g., `dev`, `val`, `prod`, or ephemeral environments for PR previews).
- **Custom Synthesizer**: Uses a custom CDK synthesizer configuration stored in AWS Parameter Store.
- **Integrated IAM Policies**: Applies IAM permissions boundaries and paths for secure resource access.
- **Ephemeral Environment Support**: Supports PR-based deployments with automatic cleanup policies.
- **Global Aspects System**: Applies global configurations like IAM paths, permissions boundaries, and removal policies.

## Project Structure
- **`bin/`**: Entry points for deploying specific stacks (e.g., `docker-lambdas.ts`, `static-assets.ts`).
- **`lib/stacks/`**: Contains stack definitions for various independent stacks like the eRegs site, the parsers, the text extractor, etc.
- **`lib/constructs/`**: Reusable constructs for common patterns like WAF and database setups.
- **`lib/aspects/`**: Custom CDK aspects for applying global configurations.
- **`config/`**: Configuration utilities for environment and stage management.
- **`utils/`**: Helper functions for tasks like fetching parameters from AWS Parameter Store.

## Deployment
### Prerequisites
- AWS CLI configured with appropriate credentials.
- Node.js and npm installed.
- Required AWS permissions to deploy CDK stacks.

### Steps
1. Install dependencies:
   ```bash
   npm install
   ```
2. Bootstrap the environment (if not already done). See the README in the bootstrap directory for details.
3. Determine your stack name and environment. Set `$ENV` to `dev`, `val`, `prod`, or `eph-1234` for an ephemeral deploy. Set `$STACK` to the name of the stack, e.g. `api`, `parser-launcher`.
4. Calculate the stack's full name:
   ```bash
   STACK_NAME=cms-eregs-$ENV-$STACK
   ```
5. Determine your entry-point filename. See the [stacks](#stacks) section.
6. Deploy a specific stack:
   ```bash
   npx cdk deploy $STACK_NAME \
      -c environment=<environment> \
      -c buildId=<optional build ID> \
      --require-approval never \
      --exclusively \
      --app "npx ts-node bin/<entry point>.ts" \
      --outputs-file <outputs filename>
   ```
   Replace `<environment>` with one of `dev`, `val`, or `prod`. For ephemeral, set `<environment>` to `dev` and use the `eph-1234` naming scheme for the stack name.

For more in-depth examples, see the Github Actions workflows located at `.github/workflows/deploy-*.yml`.

## Stacks
### 1. `RedirectApiStack`
Manages the redirect API with Lambda and API Gateway. Entry-point is "zip-lambdas.ts".

### 2. `StaticAssetsStack`
Handles static assets using S3 and CloudFront, with WAF integration. Supports infrastructure-only or infrastructure-plus-content deployments, to increase deployment efficiency. Use `-c deploymentType=infrastructure/content`. Entry-point is "static-assets.ts".

### 3. `TextExtractorStack`
Creates the Text Extractor service with Lambda and SQS. SQS URL is exported. Entry-point is "docker-lambdas.ts".

### 4. `BackendStack`
Combines API and database resources, including VPC configurations and S3 storage. Includes the regsite Lambda as well as supporting Lambdas: migrate, createsu, createdb, dropdb, and the authorizer function. Entry-point is "docker-lambdas.ts".

### 5. `ParserLauncherStack`
Schedules and invokes the eCFR and FR parser Lambda functions. Entry-point is "docker-lambdas.ts".

### 6. `EcfrParserStack`
Deploys the eCFR parser Lambda function. Entry-point is "docker-lambdas.ts".

### 7. `FrParserStack`
Deploys the Federal Register (FR) parser Lambda function. Entry-point is "docker-lambdas.ts".

### 8. `MaintenanceStack`
Deploys the so-called "maintenance API", which consists simply of a Lambda function that the production API Gateway can be quickly switched to to take down the site for maintenance or repairs. Entry-point is "zip-lambdas.ts".

## Configuration
### Environment Variables
- `DEPLOY_ENV`: Specifies the deployment environment (e.g., `dev`, `val`, and `prod`).
- `PR_NUMBER`: Used for ephemeral environments to identify the PR.

### Parameter Store
Key CDK-specific parameters are stored in AWS Parameter Store, such as:
- `/eregulations/cdk_config`: Custom synthesizer configuration.
- `/account_vars/vpc/id`: VPC ID for resource placement.

### Secrets Manager
All credentials are stored in AWS Secrets Manager. The only credentials loaded at deploy-time are for setting up the database. All others are loaded at Lambda runtime.

## Best Practices
- Use ephemeral environments for testing PRs to avoid impacting shared resources.
- Regularly update the CDK bootstrap template using the `update_template.py` script in the `bootstrap/` directory.
- Follow the resource naming conventions defined in `StageConfig` for consistency.

## Additional Resources
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [eRegs GitHub Actions Workflow](.github/workflows/update-cdk-bootstrap.yml) for automating updates.
