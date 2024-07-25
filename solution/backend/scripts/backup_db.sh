#!/bin/bash
# This script will dump the given database data to a file.
# Prompt for user input

read -p "Enter the environment you wish you backup (dev/val/prod): " ENV

if [ "$ENV" == "dev" ]; then
  LAMBDA_FUNCTION_NAME="cmcs-eregs-site-dev-reg_site"
elif [ "$ENV" == "val" ]; then
  LAMBDA_FUNCTION_NAME="cmcs-eregs-site-val-reg_site"
elif [ "$ENV" == "prod" ]; then
  LAMBDA_FUNCTION_NAME="cmcs-eregs-site-prod-reg_site"
else
  echo "Invalid environment. Exiting..."
  exit 1
fi


# Get the environment variables from the Lambda function
data=$(aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --query 'Environment.Variables.{DB_HOST:DB_HOST,DB_PORT:DB_PORT,DB_NAME:DB_NAME,DB_USER:DB_USER,DB_PASSWORD:DB_PASSWORD}' --output text)

data_array=($data)

DB_HOST=${data_array[0]}
DB_NAME=${data_array[1]}
DB_PASSWORD=${data_array[2]}
DB_PORT=${data_array[3]}
DB_USER=${data_array[4]}

# Validate if the environment variables were parsed correctly
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  echo "Failed to retrieve necessary environment variables. Exiting..."
  exit 1
fi

CURRENT_DATE=$(date +"%Y%m%d%H%M%S")
BACKUP_FILENAME="${DB_HOST}_${DB_NAME}_${CURRENT_DATE}.sql"

echo "Backing up database $DB_NAME on $DB_HOST to $BACKUP_FILENAME now..."
# Dump the database
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > $BACKUP_FILENAME

if [ $? -eq 0 ]; then
  echo "Backup successful! File saved as $BACKUP_FILENAME"
else
  echo "Backup failed!"
fi
