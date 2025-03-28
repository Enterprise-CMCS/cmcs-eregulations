#!/usr/bin/env python3

import boto3
import argparse
import re
import threading
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


# Initialize AWS clients
s3_client = boto3.client("s3")
cf_client = boto3.client("cloudformation")

# Global variables
DRY_RUN = False
DRY_RUN_SLEEP = 0.05
MAX_CONCURRENT = int((os.get_terminal_size().lines - 4) / 4)
CLI_COLUMNS = os.get_terminal_size().columns

# Thread-safe dictionary to track thread statuses
thread_status = {}
status_lock = threading.Lock()

# Thread-safe list of failed stacks
failed_stacks = []
failed_lock = threading.Lock()


def update_thread_status(**kwargs):
    thread_id = kwargs.get("thread_id", threading.get_ident())
    with status_lock:
        thread_status.setdefault(thread_id, {
            "status": "",
            "stack": None,
            "bucket": None,
            "object": None,
            "num_ellipses": 3,
        })
        for key, value in kwargs.items():
            thread_status[thread_id][key] = value

        sys.stdout.write("\033[H\033[J")  # Clear the terminal
        sys.stdout.write("Processing...\n\n")
        sys.stdout.write("Current thread statuses:\n\n")
        for i, thread in enumerate(thread_status.values()):
            if not thread["stack"]:
                sys.stdout.write(f"Thread {i+1}: Idle\n\n\n")
            else:
                sys.stdout.write(f"Thread {i+1}: {thread['status']} stack {thread['stack']}{thread['num_ellipses']*'.'}\n")
                if thread["bucket"]:
                    sys.stdout.write(f"  Bucket: {thread['bucket']}...\n")
                else:
                    sys.stdout.write("\n")
                if thread["object"]:
                    sys.stdout.write(f"  Object: {thread['object'][:(CLI_COLUMNS - 20)]}...\n")
                else:
                    sys.stdout.write("\n")
            sys.stdout.write("\n")
        sys.stdout.flush()


# Function to delete S3 objects
def delete_object(bucket_name, key):
    update_thread_status(bucket=bucket_name, object=key)
    if DRY_RUN:
        time.sleep(DRY_RUN_SLEEP)
    else:
        s3_client.delete_object(Bucket=bucket_name, Key=key)


# Delete S3 bucket
def delete_bucket(bucket_name):
    update_thread_status(bucket=bucket_name, object=None)
    if DRY_RUN:
        time.sleep(DRY_RUN_SLEEP)
    else:
        s3_client.delete_bucket(Bucket=bucket_name)


# Delete CloudFormation stack
def delete_stack_instance(stack_name):
    update_thread_status(status="Deleting", stack=stack_name, bucket=None, object=None)
    if DRY_RUN:
        time.sleep(DRY_RUN_SLEEP)
    else:
        cf_client.delete_stack(StackName=stack_name)


# Wait for stack deletion to complete
def wait_for_stack_deletion(stack_name):
    def monitor_thread_status(thread_id, stop_event):
        while not stop_event.is_set():
            time.sleep(0.5)
            ellipses = (thread_status[thread_id]["num_ellipses"] + 1) % 4
            update_thread_status(thread_id=thread_id, num_ellipses=ellipses)

    thread_id = threading.get_ident()
    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_thread_status, args=(thread_id, stop_event))
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        if DRY_RUN:
            time.sleep(10)
        else:
            waiter = cf_client.get_waiter("stack_delete_complete")
            waiter.wait(StackName=stack_name)
    finally:
        stop_event.set()
        monitor_thread.join()


# Main function to delete stacks
def delete_stack(stack):
    stack_name = stack["StackName"]
    update_thread_status(status="Processing", stack=stack_name, bucket=None, object=None)

    # Get stack resources to find S3 buckets
    resources = cf_client.describe_stack_resources(StackName=stack_name)
    for resource in resources["StackResources"]:
        if resource["ResourceType"] == "AWS::S3::Bucket":
            bucket_name = resource["PhysicalResourceId"]

            # List and delete all objects in the bucket
            try:
                objects = s3_client.list_objects_v2(Bucket=bucket_name)
                if "Contents" in objects:
                    for obj in objects["Contents"]:
                        delete_object(bucket_name, obj["Key"])

                # Delete the bucket itself
                delete_bucket(bucket_name)
            except s3_client.exceptions.NoSuchBucket:
                # Bucket already deleted
                pass
            except Exception as e:
                update_thread_status(status="Error processing", stack=stack_name, bucket=bucket_name, object=None)
                time.sleep(5) # Give the user a moment to see the error
                raise  # Re-raise the exception to skip the stack

    delete_stack_instance(stack_name)
    wait_for_stack_deletion(stack_name)


def delete_group(group):
    for stack in group:
        try:
            delete_stack(stack)
        except Exception as e:
            with failed_lock:
                failed_stacks.append(stack["StackName"])
            update_thread_status(status="Error processing", stack=stack["StackName"], bucket=None, object=None)
            time.sleep(5) # Give the user a moment to see the error
            continue # Permit the loop to continue even if one stack fails


def delete_stacks(exclude_prs):
    # List all stacks that are not currently being updated, or are already deleted
    stacks = []
    next_token = None

    while True:
        # Get the current page of stacks
        response = cf_client.list_stacks(
            StackStatusFilter=[
                "CREATE_COMPLETE",
                "UPDATE_COMPLETE",
                "ROLLBACK_COMPLETE",
                "DELETE_FAILED",
                "UPDATE_ROLLBACK_COMPLETE",
            ],
            **{"NextToken": next_token} if next_token else {}
        )

        # Append the stacks to the list
        stacks.extend(response["StackSummaries"])
        next_token = response.get("NextToken")

        # If there are no more pages, break the loop
        if not next_token:
            break

    # Reorder stacks to ensure that stacks with dependencies are deleted first
    stacks.sort(key=lambda x: x["CreationTime"], reverse=True)

    # Use regex to filter out stacks that do not contain "dev1234" or "eph-1234"
    # Then group stacks by PR number
    pattern = re.compile(r"(?:dev|eph-)(\d{4})")
    pr_groups = {}
    for stack in stacks:
        match = pattern.search(stack["StackName"])
        if match:
            pr_number = match.group(1)
            pr_groups.setdefault(pr_number, []).append(stack)

    # Exclude stacks based on PR numbers
    for pr in exclude_prs:
        if pr in pr_groups:
            del pr_groups[pr]

    # Print the list of PRs and their corresponding stacks
    for pr, group in pr_groups.items():
        print(f"PR {pr}:")
        print("  " + "\n  ".join([f"- {stack['StackName']}" for stack in group]))

    # Ask the user for confirmation
    confirmation = input("Do you want to proceed with deletion? (yes/no): ").strip().lower()
    if confirmation != "yes":
        print("Deletion process aborted by the user.")
        return

    # Process stacks in parallel with a limit on the number of concurrent executions
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = []
        for pr, group in pr_groups.items():
            futures.append(executor.submit(delete_group, group))

        for future in as_completed(futures):
            future.result()

    sys.stdout.write("\033[H\033[J")  # Clear the terminal
    print("All stacks have been processed.")
    if failed_stacks:
        print("The following stacks failed to delete:")
        for stack in failed_stacks:
            print(f"- {stack}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Delete all experimental deployments.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually deleting stacks or buckets"
    )
    parser.add_argument(
        "--exclude-prs",
        nargs="+",
        type=str,
        help="List of stacks (by PR number) to exclude from deletion"
    )
    args = parser.parse_args()

    if args.dry_run:
        DRY_RUN = True
        print("Dry run mode enabled. No AWS resources will be deleted.")

    exclude_prs = args.exclude_prs if args.exclude_prs else []

    delete_stacks(exclude_prs)
