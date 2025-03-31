#!/usr/bin/env python3

import re

import boto3

# Initialize AWS clients
s3_client = boto3.client("s3")
cf_client = boto3.client("cloudformation")


def find_orphaned_buckets():
    orphaned_buckets = []

    # Find orphaned S3 buckets
    try:
        continuation_token = None
        while True:
            response = s3_client.list_buckets(
                **{"ContinuationToken": continuation_token} if continuation_token else {},
            )

            buckets = response.get("Buckets", [])
            for bucket in buckets:
                bucket_name = bucket["Name"]
                pattern = re.compile(r"(?:dev|eph-)(\d{4})")
                match = pattern.search(bucket_name)
                if match or "eregs" in bucket_name.lower() or "serverless" in bucket_name.lower():
                    try:
                        cf_client.describe_stack_resources(PhysicalResourceId=bucket_name)
                    except cf_client.exceptions.ClientError as e:
                        if "does not exist" in str(e):
                            orphaned_buckets.append(bucket_name)

            continuation_token = response.get("ContinuationToken")
            if not continuation_token:
                break
    except Exception as e:
        print(f"Error finding orphaned S3 buckets: {e}")

    return orphaned_buckets


def find_orphaned_security_groups():
    orphaned_security_groups = []

    # Find orphaned security groups
    try:
        ec2_client = boto3.client("ec2")
        next_token = None
        while True:
            response = ec2_client.describe_security_groups(
                **{"NextToken": next_token} if next_token else {}
            )
            security_groups = response.get("SecurityGroups", [])
            for sg in security_groups:
                sg_id = sg["GroupId"]
                group_name = sg["GroupName"]
                if "eregs" in group_name.lower():
                    try:
                        cf_client.describe_stack_resources(PhysicalResourceId=sg_id)
                    except cf_client.exceptions.ClientError as e:
                        if "does not exist" in str(e):
                            orphaned_security_groups.append((sg_id, group_name))
            next_token = response.get("NextToken")
            if not next_token:
                break
    except Exception as e:
        print(f"Error finding orphaned security groups: {e}")

    return orphaned_security_groups


def find_orphaned_log_groups():
    orphaned_log_groups = []

    # Find orphaned log groups
    try:
        logs_client = boto3.client("logs")
        next_token = None
        while True:
            response = logs_client.describe_log_groups(
                **{"nextToken": next_token} if next_token else {}
            )
            log_groups = response.get("logGroups", [])
            for log_group in log_groups:
                log_group_name = log_group["logGroupName"]
                match_words = any([i in log_group_name.lower() for i in ["eregs", "eph", "serverless", "dev", "test", "redirect", "maintenance", "extractor"]])
                exclude_words = any([i in log_group_name.lower() for i in ["prod", "production", "postgres"]])
                if match_words and not exclude_words:
                    try:
                        cf_client.describe_stack_resources(PhysicalResourceId=log_group_name)
                    except cf_client.exceptions.ClientError as e:
                        if "does not exist" in str(e):
                            orphaned_log_groups.append(log_group_name)
            next_token = response.get("nextToken")
            if not next_token:
                break
    except Exception as e:
        print(f"Error finding orphaned log groups: {e}")

    return orphaned_log_groups


def delete_buckets(buckets):
    failed_buckets = []

    # Delete orphaned S3 buckets
    for bucket in buckets:
        try:
            print(f"Emptying S3 bucket: {bucket}")
            # Delete all objects in the bucket
            objects = s3_client.list_objects_v2(Bucket=bucket)
            if "Contents" in objects:
                for obj in objects["Contents"]:
                    s3_client.delete_object(Bucket=bucket, Key=obj["Key"])

            print(f"Deleting all versions in S3 bucket: {bucket}")
            # Delete all object versions (if versioning is enabled)
            versions = s3_client.list_object_versions(Bucket=bucket)
            if "Versions" in versions:
                for version in versions["Versions"]:
                    s3_client.delete_object(Bucket=bucket, Key=version["Key"], VersionId=version["VersionId"])
            if "DeleteMarkers" in versions:
                for marker in versions["DeleteMarkers"]:
                    s3_client.delete_object(Bucket=bucket, Key=marker["Key"], VersionId=marker["VersionId"])

            # Delete the bucket itself
            print(f"Deleting S3 bucket: {bucket}")
            s3_client.delete_bucket(Bucket=bucket)
        except Exception as e:
            print(f"Error deleting S3 bucket {bucket}: {e}")
            failed_buckets.append(bucket)

    if failed_buckets:
        print("\nFailed to delete the following S3 buckets:")
        for bucket in failed_buckets:
            print(f" - {bucket}")


def delete_security_groups(security_groups):
    failed_security_groups = []

    # Delete orphaned security groups
    ec2_client = boto3.client("ec2")
    for sg_id, group_name in security_groups:
        try:
            print(f"Deleting Security Group: {sg_id} ({group_name})")
            ec2_client.delete_security_group(GroupId=sg_id)
        except Exception as e:
            print(f"Error deleting Security Group {sg_id}: {e}")
            failed_security_groups.append((sg_id, group_name))

    if failed_security_groups:
        print("\nFailed to delete the following security groups:")
        for sg in failed_security_groups:
            print(f" - {sg[0]}: ({sg[1]})")


def delete_log_groups(log_groups):
    failed_log_groups = []

    # Delete orphaned log groups
    logs_client = boto3.client("logs")
    for log_group in log_groups:
        try:
            print(f"Deleting Log Group: {log_group}")
            logs_client.delete_log_group(logGroupName=log_group)
        except Exception as e:
            print(f"Error deleting Log Group {log_group}: {e}")
            failed_log_groups.append(log_group)

    if failed_log_groups:
        print("\nFailed to delete the following log groups:")
        for log_group in failed_log_groups:
            print(f" - {log_group}")


def ask_delete():
    # Ask user if they want to proceed with deletion
    proceed = input("\nDo you want to delete these orphaned resources? (yes/no): ").strip().lower()
    return proceed == "yes"


if __name__ == "__main__":
    # Find and delete orphaned S3 buckets
    buckets = find_orphaned_buckets()
    print("Found the following orphaned S3 buckets:")
    for bucket in buckets:
        print(f" - {bucket}")
    if ask_delete():
        delete_buckets(buckets)
    
    groups = find_orphaned_security_groups()
    print("\nFound the following orphaned security groups:")
    for sg in groups:
        print(f" - {sg[0]} ({sg[1]})")
    if ask_delete():
        delete_security_groups(groups)

    log_groups = find_orphaned_log_groups()
    print("\nFound the following orphaned log groups:")
    for log_group in log_groups:
        print(f" - {log_group}")
    if ask_delete():
        delete_log_groups(log_groups)

    print("\nDeletion process completed.")
