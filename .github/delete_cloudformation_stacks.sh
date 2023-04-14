 #!/bin/bash
 set -e


# Function to get the stack status
get_stack_status(stack_name) {
  aws cloudformation describe-stacks --stack-name "${stack_name}" --query 'Stacks[0].StackStatus' --output text 2> /dev/null
}

delete_stack() {
  stack_name=$1
  config=$2
  echo "check if stack exists"
  # Check if the stack exists
  STACK_EXISTS=$(get_stack_status(stack_name))
  echo "before while loop"
  while [[ "${STACK_EXISTS}" == "CREATE_IN_PROGRESS" || "${STACK_EXISTS}" == "UPDATE_IN_PROGRESS" || "${STACK_EXISTS}" == "DELETE_IN_PROGRESS" ]]; do
    echo "Waiting for the stack '${stack_name}' to finish its ongoing operation..."
    sleep 10
    STACK_EXISTS=$(get_stack_status)
  done

  echo "if stack does not exists then nothing to delete"
  if [ -z "${STACK_EXISTS}" ]; then
    echo "Stack '${stack_name}' does not exist. Nothing to delete."
  else
    echo "within stack exists and its not in in progress state delete the stack"
    # Stack exists and is not in an "in progress" state, delete the stack
    aws cloudformation delete-stack --stack-name "${stack_name}"
    echo "Deleting the stack '${stack_name}'..."
    serverless remove --stage dev${PR} --config "${config}"
    echo "Stack '${stack_name}' deleted successfully."
  fi
end
