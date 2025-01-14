# Build the image
docker build -t django-lambda -f regsite.Dockerfile . --no-cache

# Stop any existing containers
docker stop django-lambda-test 2>/dev/null
docker rm django-lambda-test 2>/dev/null

# Run the container
docker run -p 9001:8080 \
  --name django-lambda-test \
  -e DJANGO_SETTINGS_MODULE="cmcs_regulations.settings.deploy" \
  -e PYTHONPATH="/var/task" \
  -e DJANGO_CONFIGURATION="Production" \
  -e DB_NAME="eregs" \
  -e DB_USER="eregsuser" \
  -e DB_HOST="localhost" \
  -e DB_PORT="5432" \
  -e ALLOWED_HOST=".amazonaws.com,localhost" \
  -e STAGE_ENV="local" \
  -e WORKING_DIR="/var/task" \
  -e BASE_URL="http://localhost:9001" \
  -e AWS_LAMBDA_LOG_LEVEL=DEBUG \
  -e PYTHONUNBUFFERED=1 \
  -e LAMBDA_RUNTIME_DEBUG=1 \
  django-lambda