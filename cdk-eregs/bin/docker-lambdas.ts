#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { getParameterValue } from '../utils/parameter-store';
import { validateEnvironmentContext } from '../config/environment-config';
import { StageConfig } from '../config/stage-config';
import { IamPathAspect } from '../lib/aspects/iam-path';
import { IamPermissionsBoundaryAspect } from '../lib/aspects/iam-permissions-boundary-aspect';
import { EphemeralRemovalPolicyAspect } from '../lib/aspects/removal-policy-aspect';
import { FrParserStack } from '../lib/stacks/fr-parser-stack';
import { EcfrParserStack } from '../lib/stacks/ecfr-parser-stack';
import { BackendStack } from '../lib/stacks/api-stack';
import { ParserLauncherStack } from '../lib/stacks/parser-launcher-stack';

async function main() {
    const synthesizerConfig = JSON.parse(await getParameterValue('/eregulations/cdk_config'));
    
    // Fetch required infrastructure parameters
    const [
        logLevel,
        vpcId,
        privateSubnetAId,
        privateSubnetBId,
    ] = await Promise.all([
        getParameterValue('/eregulations/text_extractor/log_level'),
        getParameterValue('/account_vars/vpc/id'),
        getParameterValue('/account_vars/vpc/subnets/private/1a/id'),
        getParameterValue('/account_vars/vpc/subnets/private/1b/id'),
    ]);

    const env = { 
        account: process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID, 
        region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
    };

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

    new FrParserStack(app, stageConfig.getResourceName('fr-parser'), {
        env,
        lambdaConfig: {
            timeout: 900,
            memorySize: 1024,
        },
        environmentConfig: {
            logLevel,
        }
    }, stageConfig);
    
    new EcfrParserStack(app, stageConfig.getResourceName('ecfr-parser'), {
        env,
        lambdaConfig: {
            timeout: 900,
            memorySize: 1024,
        },
        environmentConfig: {
            logLevel,
        }
    }, stageConfig);

    new ParserLauncherStack(app, stageConfig.getResourceName('parser-launcher'), {
        env,
        lambdaConfig: {
            runtime: cdk.aws_lambda.Runtime.PYTHON_3_12,
            timeout: 900,
            memorySize: 1024,
        },
        environmentConfig: {
            secretName: "/eregulations/http/credentials",
        }
    }, stageConfig);

    new BackendStack(app, stageConfig.getResourceName('api'), {
        env,
        description: `API Stack for ${stageConfig.getResourceName('site')}`,
        lambdaConfig: {
            memorySize: 4096,
            timeout: 30,
        },
        environmentConfig: {
            vpcId,
            logLevel: process.env.LOG_LEVEL || 'INFO',
            subnetIds: [privateSubnetAId, privateSubnetBId],
        }
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
