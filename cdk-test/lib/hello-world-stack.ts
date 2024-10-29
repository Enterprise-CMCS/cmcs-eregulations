import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

// Lambda L2 construct
import * as lambda from 'aws-cdk-lib/aws-lambda';

// API Gateway L2 construct
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export class HelloWorldStack extends cdk.Stack {
  constructor(scope: Construct, id: string, stage: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const helloWorldLambda = new lambda.Function(this, `cmcs-eregs-${stage}-HelloWorldLambda`, {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'hello-world.handler',
      code: lambda.Code.fromAsset('lambda'),
    });

    const apiGateway = new apigateway.LambdaRestApi(this, `cmcs-eregs-${stage}-HelloWorldAPI`, {
      handler: helloWorldLambda,
      proxy: false,
    });

    const helloResource = apiGateway.root.addResource('hello');
    helloResource.addMethod('GET');
  }
}
