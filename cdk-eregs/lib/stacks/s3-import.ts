import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export interface S3ImportStackProps extends cdk.StackProps {
  bucketName: string;
}

export class S3ImportStack extends cdk.Stack {
  public readonly bucket: s3.IBucket;

  constructor(scope: Construct, id: string, props: S3ImportStackProps) {
    super(scope, id, props);

    // Define the imported bucket
    this.bucket = new s3.Bucket(this, 'ImportedBucket', {
      bucketName: props.bucketName,
      // Add any additional configuration you want to maintain
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      autoDeleteObjects: false,
    });

    // Output the bucket ARN
    new cdk.CfnOutput(this, 'BucketArn', {
      value: this.bucket.bucketArn,
      description: 'The ARN of the imported bucket',
    });
  }
}
