# CDK Policy Connector Infrastructure

This directory contains the AWS CDK infrastructure code for the eRegulations project.

## Prerequisites

- Node.js 18+
- Python 3.10+
- AWS CLI configured
- Docker installed and running
- AWS CDK CLI: `npm install -g aws-cdk`

## Local Development Setup

1. Install dependencies:
```bash
npm install
```

2. Bootstrap your AWS environment (if not already done):
```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

3. AWS Role Setup

To develop locally, you need the `EregsDevRole`. Create it using the GitHub Role Stack:
```bash
# Set required environment variables
export DEVELOPER_USERNAME=your-iam-username
export GITHUB_REPO_PATH=org/repo-name

# Deploy the role stack (requires admin access)
npx cdk deploy GithubActionRole
```

This creates both:
- The GitHub Actions role for CI/CD
- The EregsDevRole for local development

Ensure your IAM user has permission to assume this role by adding this policy to your user:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::891376964164:role/EregsDevRole"
        }
    ]
}
```

## Deployment

### Using the Deploy Script

The `deploy.sh` script handles building and deploying all components:

```bash
# View available options
./deploy.sh -h

# Deploy everything to production
./deploy.sh -e prod -t all

# Deploy specific components
./deploy.sh -e prod -t static    # Static assets only
./deploy.sh -e prod -t api       # API stack only
./deploy.sh -e prod -t content   # Content updates only
./deploy.sh -e prod -t parsers   # Parser lambdas only
```

### Manual Stack Deployment

If you need to deploy individual stacks:

```bash
# Deploy static assets infrastructure
cdk deploy a1m-eregs-prod-static

# Deploy API stack
cdk deploy a1m-eregs-prod-api

# Deploy parsers
cdk deploy a1m-eregs-prod-ecfr-parser a1m-eregs-prod-fr-parser
```

## Utility Scripts

### GitHub Role Setup (`bin/github-role.ts`)

Sets up OIDC authentication between GitHub Actions and AWS:

```bash
# Set required environment variables
export DEVELOPER_USERNAME=your-username
export GITHUB_REPO_PATH=org/repo-name

# Deploy the role stack
npx cdk deploy GithubActionRole
```

### Cleanup Script (`bin/cleanup.ts`)

Helps remove old resources and stacks:

```bash
# View what will be deleted
npx ts-node bin/cleanup.ts --dry-run

# Actually perform the cleanup
npx ts-node bin/cleanup.ts
```

## Project Structure

```
cdk-eregs/
├── bin/                    # CDK app entry points
│   ├── cdk-eregs.ts       # Main CDK app
│   ├── github-role.ts     # GitHub OIDC setup
│   └── cleanup.ts         # Resource cleanup
├── lib/                    # Stack definitions
│   ├── api-stack.ts       # API Gateway and Lambda
│   ├── static-stack.ts    # S3 and CloudFront
│   └── parser-stack.ts    # Parser Lambdas
├── deploy.sh              # Deployment script
└── package.json           # Dependencies
```

## CI/CD

The project uses GitHub Actions for continuous deployment. The workflow is defined in `.github/workflows/deploy.yml` and will:
- Deploy automatically on pushes to `main`
- Allow manual triggers via workflow_dispatch
- Use OIDC for secure AWS authentication

## Common Issues


### Deployment Failures
1. Check CloudFormation console for detailed error messages
2. Ensure all required environment variables are set
3. Verify AWS credentials and roles are properly configured

## Contributing

1. Create a feature branch
2. Make your changes
3. Test using `deploy.sh` with appropriate parameters
4. Submit a pull request to `main`
