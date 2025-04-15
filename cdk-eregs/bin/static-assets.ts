#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { getParameterValue } from '../utils/parameter-store';
import { validateEnvironmentContext } from '../config/environment-config';
import { StageConfig } from '../config/stage-config';
import { IamPathAspect } from '../lib/aspects/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
import { StaticAssetsStack } from '../lib/stacks/static-assets-stack';

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

    Object.entries(stageConfig.getStackTags()).forEach(([key, value]) => {
        cdk.Tags.of(app).add(key, value);
    });
    const deploymentType = app.node.tryGetContext('deploymentType') || 'content';  

    new StaticAssetsStack(app, `${stageConfig.getResourceName('static-assets')}`, {
        prNumber,
        deploymentType,  // Pass the deployment type to the stack
        env: {
            account: process.env.CDK_DEFAULT_ACCOUNT,
            region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
        },
        description: `Static assets stack for ${stageConfig.environment}`
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
