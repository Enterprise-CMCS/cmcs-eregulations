#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';

interface GithubActionRoleStackProps extends cdk.StackProps {
  developerUsername: string;
  githubRepoPath: string;
}

class GithubActionRoleStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: GithubActionRoleStackProps) {
    super(scope, id, props);

    if (!props.developerUsername) {
      throw new Error('developerUsername is required in props');
    }

    if (!props.githubRepoPath) {
      throw new Error('githubRepoPath is required in props');
    }

    // Create the GitHub OIDC Provider
    const provider = new cdk.aws_iam.OpenIdConnectProvider(this, 'GithubProvider', {
      url: 'https://token.actions.githubusercontent.com',
      clientIds: ['sts.amazonaws.com'],
      thumbprints: ['6938fd4d98bab03faadb97b34396831e3780aea1'],
    });

    // Create the GitHub Actions role
    const githubRole = new cdk.aws_iam.Role(this, 'github-action-role', {
      roleName: 'GithubActionRole',
      assumedBy: new cdk.aws_iam.WebIdentityPrincipal(
        provider.openIdConnectProviderArn,
        {
          StringLike: {
            'token.actions.githubusercontent.com:sub': `repo:${props.githubRepoPath}:*`
          }
        }
      )
    });

    // Create a developer role with the same permissions
    const devRole = new cdk.aws_iam.Role(this, 'developer-role', {
      roleName: 'EregsDevRole',
      assumedBy: new cdk.aws_iam.ArnPrincipal(`arn:aws:iam::${this.account}:user/${props.developerUsername}`),
    });

    // Create deployment policy that will be shared by both roles
    const deploymentPolicy = new cdk.aws_iam.ManagedPolicy(this, 'DeploymentPolicy', {
      statements: [
        // CloudFormation permissions for CDK
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'cloudformation:*',
          ],
          resources: ['*'],
        }),
        // Lambda permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'lambda:*',
          ],
          resources: [`arn:aws:lambda:${this.region}:${this.account}:function:a1m-eregs-*`],
        }),
        // S3 permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            's3:*',
          ],
          resources: [
            `arn:aws:s3:::a1m-eregs-*`,
            `arn:aws:s3:::a1m-eregs-*/*`,
          ],
        }),
        // CloudFront permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'cloudfront:*',
          ],
          resources: ['*'],
        }),
        // SSM Parameter Store permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'ssm:GetParameter',
            'ssm:GetParameters',
          ],
          resources: [
            `arn:aws:ssm:${this.region}:${this.account}:parameter/eregulations/*`,
            `arn:aws:ssm:${this.region}:${this.account}:parameter/account_vars/*`,
            `arn:aws:ssm:${this.region}:${this.account}:parameter/cdk-bootstrap/*`,
          ],
        }),
        // CDK Bootstrap permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'sts:AssumeRole',
          ],
          resources: [
            `arn:aws:iam::${this.account}:role/cdk-*`,
          ],
        }),
        // Additional CDK permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'cloudformation:DescribeStacks',
            'cloudformation:ListStacks',
            'cloudformation:DescribeStackEvents',
            'cloudformation:GetTemplateSummary',
            'cloudformation:ValidateTemplate',
          ],
          resources: ['*'],
        }),
        // Secrets Manager permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'secretsmanager:GetSecretValue',
            'secretsmanager:DescribeSecret',
          ],
          resources: [
            `arn:aws:secretsmanager:${this.region}:${this.account}:secret:a1m-eregs-*`,
          ],
        }),
        // RDS permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'rds:*',
          ],
          resources: [
            `arn:aws:rds:${this.region}:${this.account}:db:a1m-eregs-*`,
            `arn:aws:rds:${this.region}:${this.account}:cluster:a1m-eregs-*`,
          ],
        }),
        // CloudWatch Logs permissions
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'logs:CreateLogGroup',
            'logs:CreateLogStream',
            'logs:PutLogEvents',
          ],
          resources: [`arn:aws:logs:${this.region}:${this.account}:log-group:/aws/lambda/a1m-eregs-*`],
        }),
        // IAM permissions for role creation and permission boundaries
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'iam:CreateRole',
            'iam:DeleteRole',
            'iam:GetRole',
            'iam:PutRolePolicy',
            'iam:DeleteRolePolicy',
            'iam:AttachRolePolicy',
            'iam:DetachRolePolicy',
            'iam:TagRole',
            'iam:UntagRole',
          ],
          resources: [`arn:aws:iam::${this.account}:role/delegatedadmin/developer/*`],
        }),
        // Permission boundary policies
        new cdk.aws_iam.PolicyStatement({
          effect: cdk.aws_iam.Effect.ALLOW,
          actions: [
            'iam:GetPolicy',
            'iam:GetPolicyVersion',
          ],
          resources: [
            `arn:aws:iam::${this.account}:policy/cms-cloud-admin/developer-boundary-policy`,
            `arn:aws:iam::${this.account}:policy/cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy`,
          ],
        }),
      ],
    });

    // Add the policy to both roles
    githubRole.addManagedPolicy(deploymentPolicy);
    devRole.addManagedPolicy(deploymentPolicy);

    // Output both role ARNs
    new cdk.CfnOutput(this, 'GithubRoleArn', {
      value: githubRole.roleArn,
      description: 'ARN of role for GitHub Actions',
      exportName: 'GithubActionRoleArn',
    });

    new cdk.CfnOutput(this, 'DevRoleArn', {
      value: devRole.roleArn,
      description: 'ARN of role for local development',
      exportName: 'EregsDevRoleArn',
    });
  }
}

// Get environment variables with validation
const developerUsername = process.env.DEVELOPER_USERNAME;
const githubRepoPath = process.env.GITHUB_REPO_PATH;

if (!developerUsername) {
  throw new Error('DEVELOPER_USERNAME environment variable is required');
}

if (!githubRepoPath) {
  throw new Error('GITHUB_REPO_PATH environment variable is required');
}

const app = new cdk.App();
new GithubActionRoleStack(app, 'GithubActionRole', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  developerUsername,
  githubRepoPath,
});
app.synth();