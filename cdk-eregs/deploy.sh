#!/bin/bash

# Constants for static asset builds
export VITE_ENV="prod"
export VITE_API_URL="https://ytb5df0j70.execute-api.us-east-1.amazonaws.com/prod/"
export STATIC_ROOT="../static-assets/regulations"
export STATIC_URL="https://d2u4e5ix6gh9z7.cloudfront.net"
export DOCKER_CLIENT_TIMEOUT=2000

# Function to print usage
print_usage() {
    echo "Usage: $0 [-h] [-e environment] [-t type]"
    echo "  -h: Show this help message"
    echo "  -e: Environment (default: prod)"
    echo "  -t: Deployment type (static|api|content|parsers|text-extractor|all)"
    echo "      all: Deploy everything in correct order"
    echo "      static: Deploy static assets infrastructure"
    echo "      api: Deploy API stack"
    echo "      content: Deploy content updates"
    echo "      parsers: Deploy and invoke parsers"
    echo "      text-extractor: Deploy text extractor lambda"
}

# Default values
ENVIRONMENT="prod"
DEPLOY_TYPE="all"

# Parse command line arguments
while getopts "he:t:" opt; do
    case $opt in
    h)
        print_usage
        exit 0
        ;;
    e)
        ENVIRONMENT="$OPTARG"
        ;;
    t)
        DEPLOY_TYPE="$OPTARG"
        ;;
    \?)
        print_usage
        exit 1
        ;;
    esac
done

# Validate deploy type
valid_types=("all" "static" "api" "content" "parsers" "text-extractor")
if [[ ! " ${valid_types[@]} " =~ " ${DEPLOY_TYPE} " ]]; then
    echo "Error: Invalid deployment type: ${DEPLOY_TYPE}"
    print_usage
    exit 1
fi

# Function to check if previous command succeeded
check_error() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Function to check dependencies
check_dependencies() {
    echo "Checking dependencies..."

    # List of required commands
    local deps=("aws" "node" "npm" "python")

    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            echo "Error: $cmd is not installed"
            return 1
        fi
    done

    # Verify AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo "Error: AWS credentials not configured. Run 'aws configure'"
        return 1
    fi

    echo "All dependencies found"
    return 0
}

# Function to deploy static assets infrastructure
deploy_static() {
    echo "Deploying static assets infrastructure..."
    npm run cdk deploy "a1m-eregs-${ENVIRONMENT}-static" -- \
        --app "npx ts-node --prefer-ts-exts bin/cdk-eregs.ts" \
        -c environment=${ENVIRONMENT} \
        -c deploymentType=infrastructure \
        --require-approval never
    check_error "Static assets infrastructure deployment failed"
}

# Function to deploy API stack
deploy_api() {
    echo "Deploying API stack..."
    npm run cdk deploy "a1m-eregs-${ENVIRONMENT}-api" -- \
        --app "npx ts-node --prefer-ts-exts bin/cdk-eregs.ts" \
        -c environment=${ENVIRONMENT} \
        --require-approval never
    check_error "API deployment failed"
}

# Function to deploy content
deploy_content() {
    echo "Building Vue app..."
    cd ../solution  && make regulations
    check_error "Vue app build failed"

    echo "Setting up Python virtual environment and collecting static files..."
    cd ../solution/backend || exit 1
    python -m venv venv
    venv/bin/pip install -r requirements_tmp.txt
    check_error "Python setup failed"

    venv/bin/python manage.py collectstatic --noinput
    check_error "Django collectstatic failed"

    deactivate
    cd ../../cdk-eregs || exit 1

    echo "Deploying content to CloudFront..."
    npm run cdk deploy "a1m-eregs-${ENVIRONMENT}-static" -- \
        --app "npx ts-node --prefer-ts-exts bin/cdk-eregs.ts" \
        -c environment=${ENVIRONMENT} \
        -c deploymentType=content \
        --require-approval never
    check_error "Content deployment failed"
}

# Function to deploy and invoke parsers
deploy_parsers() {
    echo "Deploying parsers..."
    npm run cdk deploy "a1m-eregs-${ENVIRONMENT}-ecfr-parser" "a1m-eregs-${ENVIRONMENT}-fr-parser" -- \
        --app "npx ts-node --prefer-ts-exts bin/cdk-eregs.ts" \
        -c environment=${ENVIRONMENT} \
        --require-approval never
    check_error "Parser deployment failed"
}

# Function to deploy text extractor
deploy_text_extractor() {
    echo "Deploying text extractor..."
    npm run cdk deploy "a1m-eregs-${ENVIRONMENT}-text-extractor" -- \
        --app "npx ts-node --prefer-ts-exts bin/cdk-eregs.ts" \
        -c environment=${ENVIRONMENT} \
        --require-approval never
    check_error "Text extractor deployment failed"
}

# Main deployment logic
echo "Starting deployment for environment: ${ENVIRONMENT}"
echo "Deployment type: ${DEPLOY_TYPE}"

# Check dependencies before proceeding
check_dependencies
check_error "Dependency check failed"

# Ensure we're in the cdk-eregs directory
cd "$(dirname "$0")"

# Install and build if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    check_error "npm install failed"
fi

echo "Building CDK project..."
# npm run build
# check_error "CDK build failed"

# Execute requested deployment type
case $DEPLOY_TYPE in
"all")
    deploy_static
    deploy_text_extractor
    deploy_api
    deploy_content
    deploy_parsers
    ;;
"static")
    deploy_static
    ;;
"api")
    deploy_api
    ;;
"content")
    deploy_content
    ;;
"parsers")
    deploy_parsers
    ;;
"text-extractor")
    deploy_text_extractor
    ;;
esac

echo "Deployment completed successfully!"
exit 0
