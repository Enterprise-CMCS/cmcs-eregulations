 #!/bin/bash
 set -e
 set -x

# Function to get the stack status
STACK_NAME=$1
PR=$2
CONFIG=$3

echo $STACK_NAME
echo $PR
echo $CONFIG

# Function to get the stack status
# Function to get the stack status
get_stack_status() {
  aws --debug cloudformation describe-stacks --stack-name "${STACK_NAME}" --query 'Stacks[0].StackStatus' --output text 2> /dev/null
}

# Check if the stack exists

if aws cloudformation describe-stacks --stack-name "$STACK_NAME" > /dev/null 2>&1; then
    STACK_EXISTS=$(get_stack_status)
    echo "Stack status: $stack_status"
    while [[ "${STACK_EXISTS}" == "CREATE_IN_PROGRESS" || "${STACK_EXISTS}" == "UPDATE_IN_PROGRESS" || "${STACK_EXISTS}" == "DELETE_IN_PROGRESS" ]]; do
      echo "Waiting for the stack '${STACK_NAME}' to finish its ongoing operation..."
      sleep 10
      STACK_EXISTS=$(get_stack_status)
    done

   # Stack exists and is not in an "in progress" state, delete the stack
   echo "Deleting the stack '${STACK_NAME}'..."
   serverless remove --stage dev${PR} --config ${CONFIG}
   aws --debug cloudformation wait stack-delete-complete --stack-name ${STACK_NAME}
   echo "Stack '${STACK_NAME}' deleted successfully."
else
   echo "Stack '${STACK_NAME}' does not exist. Nothing to delete."
fi
