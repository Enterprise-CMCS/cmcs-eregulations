#!/bin/sh

echo "Script is running"

# Get the CloudFront distribution ID from Serverless Framework configuration
DISTRIBUTION_ID=$(serverless print | jq -r '.resources.Resources.CloudFrontDistribution.Properties.DistributionId')
echo "Distribution ID: $DISTRIBUTION_ID"

# Replace AWS_REGION with your AWS region (e.g., us-east-1)
AWS_REGION="us-east-1"

# Replace DEFAULT_ROOT_OBJECT with your desired default root object (e.g., index.html)
DEFAULT_ROOT_OBJECT="index.html"
echo "Default Root Object: $DEFAULT_ROOT_OBJECT"

# Update the CloudFront distribution with the default root object
aws cloudfront update-distribution --id $DISTRIBUTION_ID --default-root-object $DEFAULT_ROOT_OBJECT --region $AWS_REGION

# Invalidate CloudFront cache for all files
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" --region $AWS_REGION
echo "Cache invalidation triggered"
