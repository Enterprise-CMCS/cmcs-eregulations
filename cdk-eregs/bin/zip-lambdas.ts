#!/usr/bin/env node

import * as cdk from 'aws-cdk-lib';
import { getParameterValue } from '../utils/parameter-store';
import { validateEnvironmentContext } from '../config/environment-config';
import { RedirectApiStack } from '../lib/stacks/redirect-stack';
import { StageConfig } from '../config/stage-config';
import { IamPathAspect } from '../lib/aspects/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { MaintenanceApiStack } from '../lib/stacks/maintainance-stack';


async function main() {
    const synthesizerConfig = JSON.parse(await getParameterValue('/eregulations/cdk_config'));

    const app = new cdk.App({
        defaultStackSynthesizer: new cdk.DefaultStackSynthesizer(synthesizerConfig),
    });

    const environment = app.node.tryGetContext('environment') || 
        process.env.DEPLOY_ENV || 
        process.env.GITHUB_JOB_ENVIRONMENT || 
        'dev';
    const prNumber = process.env.PR_NUMBER || '';
    const ephemeralId = prNumber ? `eph-${prNumber}` : undefined;

    const context = validateEnvironmentContext(
        environment,
        ephemeralId,
        process.env.GITHUB_REF,
        prNumber
    );

    const stageConfig = await StageConfig.create(
        context.environment,
        ephemeralId,
        synthesizerConfig.iamPermissionsBoundary
    );

    const tags = stageConfig.getStackTags();
    Object.entries(tags).forEach(([key, value]) => {
        cdk.Tags.of(app).add(key, value);
    });

    // Create ZIP-based Lambda stacks

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

    new MaintenanceApiStack(app, stageConfig.getResourceName('maintenance-api'), {
        lambdaConfig: {
            runtime: lambda.Runtime.PYTHON_3_12,
            memorySize: 1024,
            timeout: 30,
        },
        apiConfig: {
            loggingLevel: cdk.aws_apigateway.MethodLoggingLevel.INFO,
        },
    }, stageConfig);

    await applyGlobalAspects(app, stageConfig);

    app.synth();
}

async function applyGlobalAspects(app: cdk.App, stageConfig: StageConfig): Promise<void> {
    cdk.Aspects.of(app).add(new IamPathAspect(await getParameterValue(`/account_vars/iam/path`)));
    cdk.Aspects.of(app).add(new IamPermissionsBoundaryAspect(stageConfig.permissionsBoundaryArn));
    cdk.Aspects.of(app).add(new EphemeralRemovalPolicyAspect(stageConfig));
}

main().catch(error => {
    console.error('Error initializing CDK app:', error);
    process.exit(1);
});
