# CDK Infrastructure Technical Documentation

## Overview

This document outlines the CDK infrastructure implementation focusing on environment-aware deployments, custom synthesizers, AWS Parameter Store integration, and stack creation patterns.

## Core Components

```typescript
// app.ts
const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
const synthesizerConfig = JSON.parse(synthesizerConfigJson);

// Development Environment
const devConfig = await StageConfig.create(
  'dev',                                        // environment
  undefined,                                    // no ephemeralId
  synthesizerConfig.iamPermissionsBoundary      // from synthesizer config
);

// Example outputs:
devConfig.getResourceName('api')                // "cms-eregs-dev-api"
devConfig.aws.lambda('function')                // "/aws/lambda/cms-eregs-dev-function"
devConfig.isEphemeral()                         // false
devConfig.getStackTags()                        // { Environment: 'dev', Project: 'cms-eregs', ... }

// Production Environment
const prodConfig = await StageConfig.create(
  'prod',
  undefined,
  synthesizerConfig.iamPermissionsBoundary
);

// Example outputs:
prodConfig.getResourceName('api')               // "cms-eregs-prod-api"
prodConfig.aws.lambda('function')               // "/aws/lambda/cms-eregs-prod-function"
prodConfig.isEphemeral()                        // false
```

### 1. Stage Configuration (lib/config/stage-config.ts)

```typescript
export class StageConfig {
  public static readonly projectName = 'cms-eregs';

  public static async create(
    environment: string, 
    ephemeralId?: string,
    synthesizerPermissionsBoundary?: string
  ): Promise<StageConfig>
```

Key Features:

- Environment-aware resource naming
- Ephemeral environment support (PR-based deployments)
- AWS service-specific naming conventions
- Integrated IAM permissions boundary
- Automatic tagging system

Resource Naming Patterns:
```
// Regular environments:
{project}-{environment}-{resource}        // cms-eregs-dev-api
// Ephemeral environments:
{project}-eph-{pr-number}-{resource}     // cms-eregs-eph-123-api
// AWS Service Resources:
/aws/{service}/{project}-{environment}-{resource}
```

### 2. Application Entry Point (bin/app.ts)

```typescript
async function main() {
  // Environment Resolution Chain:
  // 1. CDK Context (-c environment=dev)
  // 2. Environment Variable (DEPLOY_ENV)
  // 3. GitHub Environment (GITHUB_JOB_ENVIRONMENT)
  // 4. Default ('dev')
  const environment = app.node.tryGetContext('environment') || 
                     process.env.DEPLOY_ENV || 
                     process.env.GITHUB_JOB_ENVIRONMENT || 
                     'dev';
```

Features:

- Custom synthesizer configuration from Parameter Store
- Environment context validation
- Global tag application
- Aspect-based IAM configuration
- Debug logging system

### 3. AWS Parameter Store Integration

```typescript
// Synthesizer Configuration
const synthesizerConfigJson = await getParameterValue('/cms/cloud/cdkSynthesizerConfig');
```

Parameter Structure:
```json
{
  "deployRoleArn": "arn:aws:iam::ACCOUNT:role/delegatedadmin/developer/cdk-deploy-role",
  "fileAssetPublishingRoleArn": "arn:aws:iam::ACCOUNT:role/delegatedadmin/developer/cdk-file-publishing-role",
  "imageAssetPublishingRoleArn": "arn:aws:iam::ACCOUNT:role/delegatedadmin/developer/cdk-image-publishing-role",
  "cloudFormationExecutionRole": "arn:aws:iam::ACCOUNT:role/delegatedadmin/developer/cdk-cfn-exec-role",
  "lookupRoleArn": "arn:aws:iam::ACCOUNT:role/delegatedadmin/developer/cdk-lookup-role",
  "qualifier": "one",
  "iamPermissionsBoundary": "arn:aws:iam::ACCOUNT:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy"
}
```

### 4. Global Aspects System

```typescript
async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
  const iamPath = await getParameterValue(`/account_vars/iam/path`);
  
  cdk.Aspects.of(app).add(new IamPathAspect(iamPath));
  cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(stageConfig.permissionsBoundaryArn));
  cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));
}
```

Available Aspects:

- **IamPathAspect**: Enforces IAM resource paths
- **IamPermissionsBoundaryAspect**: Applies IAM permissions boundaries
- **EphemeralRemovalPolicyAspect**: Manages resource cleanup for ephemeral environments

### 5. Environment-Aware Stack Creation

```typescript
new RedirectApiStack(app, stageConfig.getResourceName('redirect-api'), {
  lambdaConfig: {
    runtime: lambda.Runtime.PYTHON_3_12,
    memorySize: 1024,
    timeout: 30,
  },
  apiConfig: {
    loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
  },
}, stageConfig);
```

## Deployment Patterns

### 1. Regular Environment Deployment

```bash
# Using CDK context
cdk deploy "*redirect-api" -c environment=dev

# Using environment variable
DEPLOY_ENV=dev cdk deploy "*redirect-api"
```

### 2. PR/Ephemeral Environment Deployment

```bash
# Using PR number
PR_NUMBER=123 cdk deploy "*redirect-api" -c environment=dev

# Debug mode
CDK_DEBUG=true PR_NUMBER=123 cdk deploy "*redirect-api" -c environment=dev
```

### 3. GitHub Actions Integration

```yaml
deploy-redirect-api:
  environment:
    name: "dev"
  runs-on: ubuntu-22.04
  steps:
    - name: Deploy Stack
      env:
        PR_NUMBER: ${{ github.event.pull_request.number }}
        CDK_DEBUG: true
      run: |
        npx cdk deploy "*redirect-api" \
          -c environment=${{ environment.name }} \
          --require-approval never
```

## Debug and Logging

### 1. Debug Output Structure

```typescript
// Synthesizer Configuration
{
  permissionsBoundary: "arn:aws:iam::ACCOUNT:policy/boundary",
  environment: "dev",
  ephemeralId: "eph-123"
}

// Stage Configuration
{
  environment: "dev",
  permissionsBoundary: "arn:aws:iam::ACCOUNT:policy/boundary",
  isEphemeral: true,
  ephemeralId: "eph-123"
}

// Applied Aspects
{
  environment: "dev",
  iamPath: "/delegatedadmin/developer/",
  permissionsBoundary: "arn:aws:iam::ACCOUNT:policy/boundary",
  isEphemeral: true
}
```

## Resource Naming Conventions

### 1. AWS Service Resources

```typescript
// Lambda Functions
stageConfig.aws.lambda('function-name')
// Output: /aws/lambda/cms-eregs-dev-function-name

// API Gateway
stageConfig.aws.apiGateway('api-name')
// Output: /aws/api-gateway/cms-eregs-dev-api-name

// CloudWatch Logs
stageConfig.aws.cloudwatch('log-group-name')
// Output: /aws/cloudwatch/cms-eregs-dev-log-group-name
```

### 2. Stack Resources

```typescript
stageConfig.getResourceName('resource-name')
// Regular: cms-eregs-dev-resource-name
// Ephemeral: cms-eregs-eph-123-resource-name
```

## Best Practices

### Environment Management:

- Use CDK context for environment specification
- Implement fallback chain for environment resolution
- Validate environments before deployment

### Resource Naming:

- Use StageConfig methods for consistent naming
- Follow AWS service-specific naming patterns
- Include environment/PR identifiers in resource names

### IAM Configuration:

- Apply permissions boundaries consistently
- Use IAM path prefixing for resource organization
- Implement least privilege access

### Ephemeral Environments:

- Implement cleanup policies
- Use PR numbers for unique identification
- Apply appropriate resource retention policies
