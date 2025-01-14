import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as fs from 'fs-extra';
import { DockerImage } from 'aws-cdk-lib';
import { StageConfig } from '../../config/stage-config';

export interface PythonLayerStackProps extends cdk.StackProps {
  requirementsPath?: string;
  pythonVersion?: string;
}

export class PythonLayerStack extends cdk.Stack {
  public readonly layer: lambda.LayerVersion;
  private readonly stageConfig: StageConfig;

  constructor(scope: Construct, id: string, props: PythonLayerStackProps, stageConfig: StageConfig) {
    super(scope, id, props);
    this.stageConfig = stageConfig;

    const pythonVersion = props.pythonVersion || '3.12';
    const runtime = this.getPythonRuntime(pythonVersion);

    const requirementsPath = props.requirementsPath || path.join(__dirname, '../../../solution/static-assets/requirements.txt');
    if (!fs.existsSync(requirementsPath)) {
      throw new Error(`The specified requirements file does not exist: ${requirementsPath}`);
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const buildContext = path.join(__dirname, `layer-build-${timestamp}`);

    try {
      // Create build context
      fs.mkdirpSync(buildContext);
      fs.copyFileSync(requirementsPath, path.join(buildContext, 'requirements.txt'));

      // Create Dockerfile with more robust package installation
      fs.writeFileSync(path.join(buildContext, 'Dockerfile'), `
FROM public.ecr.aws/lambda/python:${pythonVersion}

WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt \
    -t /asset/python/lib/python${pythonVersion}/site-packages \
    --no-cache-dir --no-warn-script-location || \
    (echo "Failed to install Python packages" && exit 1)

# Cleanup unnecessary files
RUN find /asset/python -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /asset/python -type f -name "*.pyc" -delete && \
    find /asset/python -type f -name "*.pyo" -delete && \
    find /asset/python -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /asset/python -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true

# Verify package installation
RUN python3 -m pip list && \
    echo "Installed packages in /asset/python:" && \
    ls -la /asset/python/lib/python${pythonVersion}/site-packages

CMD [ "bash" ]
      `);

      // Build Docker image with enhanced error handling
      let image: DockerImage;
      try {
        image = DockerImage.fromBuild(buildContext, {
          buildArgs: {
            PIP_DISABLE_PIP_VERSION_CHECK: '1',
          },
        });
      } catch (error) {
        const err = error as Error;
        console.error('Docker build failed:', err.message);
        throw new Error(`Failed to build Docker image: ${err.message}`);
      }

      // Create Lambda Layer with improved bundling
      this.layer = new lambda.LayerVersion(this, 'PythonLayer', {
        layerVersionName: this.stageConfig.getResourceName('python-django'),
        description: `Django requirements layer (Python ${pythonVersion}, Docker-built)`,
        code: lambda.Code.fromAsset(buildContext, {
          bundling: {
            image,
            command: [
              'bash', 
              '-c', 
              'mkdir -p /asset-output && ' +
              'if [ -d "/asset/python" ]; then ' +
              '  cp -r /asset/python /asset-output/ && ' +
              '  echo "Copied python packages to /asset-output" && ' +
              '  ls -la /asset-output/python; ' +
              'else ' +
              '  echo "Error: /asset/python directory does not exist"; ' +
              '  exit 1; ' +
              'fi'
            ],
            environment: {
              PIP_DISABLE_PIP_VERSION_CHECK: '1',
            },
          },
        }),
        compatibleRuntimes: [runtime],
        removalPolicy: cdk.RemovalPolicy.RETAIN,
      });

      // Export layer ARN
      new cdk.CfnOutput(this, 'LayerVersionArn', {
        value: this.layer.layerVersionArn,
        description: 'ARN of the Python Lambda Layer',
        exportName: this.stageConfig.getResourceName('python-layer-arn'),
      });

    } catch (error) {
      const err = error as Error;
      console.error('Failed to create Python layer:', err.message);
      throw err;
    } finally {
      try {
        // Optional: Add a delay before cleanup to allow for potential debugging
        // fs.removeSync(buildContext);
        console.log(`Build context created at: ${buildContext}. Remember to clean up manually.`);
      } catch (error) {
        const err = error as Error;
        console.warn(`Failed to clean up build context: ${err.message}`);
      }
    }
  }

  private getPythonRuntime(version: string): lambda.Runtime {
    const runtimeMap: { [key: string]: lambda.Runtime } = {
      '3.7': lambda.Runtime.PYTHON_3_7,
      '3.8': lambda.Runtime.PYTHON_3_8,
      '3.9': lambda.Runtime.PYTHON_3_9,
      '3.10': lambda.Runtime.PYTHON_3_10,
      '3.11': lambda.Runtime.PYTHON_3_11,
      '3.12': lambda.Runtime.PYTHON_3_12,
    };

    const runtime = runtimeMap[version];
    if (!runtime) {
      throw new Error(`Unsupported Python version: ${version}. Supported versions are: ${Object.keys(runtimeMap).join(', ')}`);
    }

    return runtime;
  }
}