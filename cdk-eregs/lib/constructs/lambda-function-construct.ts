// lib/constructs/lambda-function-construct.ts

// import * as cdk from 'aws-cdk-lib';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as ec2 from 'aws-cdk-lib/aws-ec2';
// import * as path from 'path';
// import { Construct } from 'constructs';

// // Define defaults as constants
// const DEFAULT_TIMEOUT = cdk.Duration.seconds(900);
// const DEFAULT_MEMORY_SIZE = 128;

// // Define a type for environment variables
// // This ensures that STAGE is always present in the environment
// type LambdaEnvironment = {
//   [key: string]: string;
//   STAGE: string;
// };

// // Define interfaces for common Lambda properties
// interface CommonLambdaProps {
//   functionName: string;
//   vpc: ec2.IVpc;
//   timeout: cdk.Duration;
//   memorySize: number;
//   reservedConcurrentExecutions?: number;
//   environment: LambdaEnvironment;
// }

// // Base properties for all Lambda functions
// export interface LambdaFunctionConstructPropsBase extends Omit<lambda.FunctionOptions, 'code' | 'handler' | 'runtime'> {
//   functionName: string;
//   stage: string;
//   vpc: ec2.IVpc;
//   timeout?: cdk.Duration;
//   memorySize?: number;
//   environment: LambdaEnvironment;
// }

// // Properties specific to Docker-based Lambda functions
// export interface DockerLambdaFunctionConstructProps extends LambdaFunctionConstructPropsBase {
//   codeType: 'docker';
//   dockerImagePath: string;
// }

// // Properties specific to ZIP-based Lambda functions
// export interface ZipLambdaFunctionConstructProps extends LambdaFunctionConstructPropsBase {
//   codeType: 'zip';
//   codePath: string;
//   handler: string;
//   runtime: lambda.Runtime;
// }

// // Union type for all possible Lambda function properties
// export type LambdaFunctionConstructProps = DockerLambdaFunctionConstructProps | ZipLambdaFunctionConstructProps;

// export class LambdaFunctionConstruct extends Construct {
//   public readonly function: lambda.Function;

//   constructor(scope: Construct, id: string, props: LambdaFunctionConstructProps) {
//     super(scope, id);

//     // Create the appropriate type of Lambda function based on the codeType
//     if (props.codeType === 'docker') {
//       this.function = this.createDockerFunction(props);
//     } else {
//       this.function = this.createZipFunction(props);
//     }
//   }

//   // Helper method to get common properties for all Lambda functions
//   private getCommonProps(props: LambdaFunctionConstructProps): CommonLambdaProps {
//     return {
//       functionName: `${props.stage}-${props.functionName}`,
//       vpc: props.vpc,
//       timeout: props.timeout || DEFAULT_TIMEOUT,
//       memorySize: props.memorySize || DEFAULT_MEMORY_SIZE,
//       reservedConcurrentExecutions: props.reservedConcurrentExecutions,
//       environment: props.environment,
//     };
//   }

//   // Create a Docker-based Lambda function
//   private createDockerFunction(props: DockerLambdaFunctionConstructProps): lambda.DockerImageFunction {
//     const commonProps = this.getCommonProps(props);
//     const constructId = this.generateConstructId(props, 'Docker');

//     return new lambda.DockerImageFunction(this, constructId, {
//       ...commonProps,
//       code: lambda.DockerImageCode.fromImageAsset(props.dockerImagePath),
//     });
//   }

//   // Create a ZIP-based Lambda function
//   private createZipFunction(props: ZipLambdaFunctionConstructProps): lambda.Function {
//     const commonProps = this.getCommonProps(props);
//     const constructId = this.generateConstructId(props, 'Zip');

//     return new lambda.Function(this, constructId, {
//       ...commonProps,
//       handler: props.handler,
//       runtime: props.runtime,
//       code: lambda.Code.fromAsset(props.codePath),
//     });
//   }

//   // Generate a unique construct ID for the Lambda function
//   private generateConstructId(props: LambdaFunctionConstructProps, type: 'Docker' | 'Zip'): string {
//     const hash = cdk.Names.uniqueId(this).slice(-6);
//     return `${props.functionName}-${type}-${props.stage}-${hash}`;
//   }
// }

// lib/constructs/lambda-function-construct.ts

import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

// Define defaults as constants
const DEFAULT_TIMEOUT = cdk.Duration.seconds(900);
const DEFAULT_MEMORY_SIZE = 128;

// Define a type for environment variables
type LambdaEnvironment = {
  [key: string]: string;
  STAGE: string;
};

// Base properties for all Lambda functions
export interface LambdaFunctionConstructPropsBase extends Omit<lambda.FunctionOptions, 'code' | 'handler' | 'runtime'> {
  functionName: string;
  stage: string;
  vpc?: ec2.IVpc;  // Make VPC optional
  timeout?: cdk.Duration;
  memorySize?: number;
  environment: LambdaEnvironment;
  role?: iam.IRole;  // Make role optional
}

// Properties specific to Docker-based Lambda functions
export interface DockerLambdaFunctionConstructProps extends LambdaFunctionConstructPropsBase {
  codeType: 'docker';
  dockerImagePath: string;
}

// Properties specific to ZIP-based Lambda functions
export interface ZipLambdaFunctionConstructProps extends LambdaFunctionConstructPropsBase {
  codeType: 'zip';
  codePath: string;
  handler: string;
  runtime: lambda.Runtime;
}

// Union type for all possible Lambda function properties
export type LambdaFunctionConstructProps = DockerLambdaFunctionConstructProps | ZipLambdaFunctionConstructProps;

export class LambdaFunctionConstruct extends Construct {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: LambdaFunctionConstructProps) {
    super(scope, id);

    // Create the appropriate type of Lambda function based on the codeType
    if (props.codeType === 'docker') {
      this.function = this.createDockerFunction(props);
    } else {
      this.function = this.createZipFunction(props);
    }
  }

  private getCommonProps(props: LambdaFunctionConstructProps): lambda.FunctionProps {
    const commonProps: lambda.FunctionProps = {
      functionName: `${props.stage}-${props.functionName}`,
      timeout: props.timeout || DEFAULT_TIMEOUT,
      memorySize: props.memorySize || DEFAULT_MEMORY_SIZE,
      environment: props.environment,
    };

    if (props.vpc) {
      commonProps.vpc = props.vpc;
    }

    if (props.role) {
      commonProps.role = props.role;
    }

    return commonProps;
  }

  private createDockerFunction(props: DockerLambdaFunctionConstructProps): lambda.DockerImageFunction {
    const commonProps = this.getCommonProps(props);
    const constructId = this.generateConstructId(props, 'Docker');

    return new lambda.DockerImageFunction(this, constructId, {
      ...commonProps,
      code: lambda.DockerImageCode.fromImageAsset(props.dockerImagePath),
    });
  }

  private createZipFunction(props: ZipLambdaFunctionConstructProps): lambda.Function {
    const commonProps = this.getCommonProps(props);
    const constructId = this.generateConstructId(props, 'Zip');

    return new lambda.Function(this, constructId, {
      ...commonProps,
      handler: props.handler,
      runtime: props.runtime,
      code: lambda.Code.fromAsset(props.codePath),
    });
  }

  private generateConstructId(props: LambdaFunctionConstructProps, type: 'Docker' | 'Zip'): string {
    const hash = cdk.Names.uniqueId(this).slice(-6);
    return `${props.functionName}-${type}-${props.stage}-${hash}`;
  }
}