#!/usr/bin/env python3

import boto3


def find_orphaned_resources():
    orphaned_buckets = []
    orphaned_security_groups = []
    orphaned_log_groups = []

    # Find orphaned S3 buckets
    try:
        buckets = s3_client.list_buckets()["Buckets"]
        for bucket in buckets:
            bucket_name = bucket["Name"]
            try:
                cf_client.describe_stack_resources(PhysicalResourceId=bucket_name)
            except cf_client.exceptions.ClientError as e:
                if "does not exist" in str(e):
                    orphaned_buckets.append(bucket_name)
    except Exception as e:
        logger.error(f"Error finding orphaned S3 buckets: {e}")

    # Find orphaned security groups
    try:
        ec2_client = boto3.client("ec2")
        security_groups = ec2_client.describe_security_groups()["SecurityGroups"]
        for sg in security_groups:
            sg_id = sg["GroupId"]
            try:
                cf_client.describe_stack_resources(PhysicalResourceId=sg_id)
            except cf_client.exceptions.ClientError as e:
                if "does not exist" in str(e):
                    orphaned_security_groups.append(sg_id)
    except Exception as e:
        logger.error(f"Error finding orphaned security groups: {e}")

    # Find orphaned log groups
    try:
        logs_client = boto3.client("logs")
        log_groups = logs_client.describe_log_groups()["logGroups"]
        for log_group in log_groups:
            log_group_name = log_group["logGroupName"]
            try:
                cf_client.describe_stack_resources(PhysicalResourceId=log_group_name)
            except cf_client.exceptions.ClientError as e:
                if "does not exist" in str(e):
                    orphaned_log_groups.append(log_group_name)
    except Exception as e:
        logger.error(f"Error finding orphaned log groups: {e}")

    logger.info(f"Orphaned S3 buckets: {orphaned_buckets}")
    logger.info(f"Orphaned security groups: {orphaned_security_groups}")
    logger.info(f"Orphaned log groups: {orphaned_log_groups}")

    return {
        "orphaned_buckets": orphaned_buckets,
        "orphaned_security_groups": orphaned_security_groups,
        "orphaned_log_groups": orphaned_log_groups,
    }
