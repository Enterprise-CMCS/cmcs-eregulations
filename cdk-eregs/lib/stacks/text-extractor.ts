import * as cdk from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';

export class TextExtractorQueueStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the SQS Queue
    const queue = new sqs.Queue(this, 'TextExtractorQueue', {
      queueName: `${this.stackName}-text-extractor-queue`,
      visibilityTimeout: cdk.Duration.seconds(900),       // 15 minutes
      retentionPeriod: cdk.Duration.days(4),              // 4 days retention
      delaySeconds: 0                                     // No initial delay
    });

    // Output SQS Queue URL and ARN
    new cdk.CfnOutput(this, 'TextExtractorQueueUrl', { value: queue.queueUrl });
    new cdk.CfnOutput(this, 'TextExtractorQueueArn', { value: queue.queueArn });
  }
}
