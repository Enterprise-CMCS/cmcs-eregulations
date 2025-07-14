#!/bin/bash
set -e

# This script deletes the database and then restores it from backup.
# Before running this script make a backup of the data you want to restore with pg_dump.
# This script does make a backup of the data it's restoring but its recommended to backup that data as well.
# you can also use backup_db.sh to do the backup. Once you have the backup file run this script

# Function to display warning message and get user confirmation
confirm_action() {
    read -p "$1 Do you wish to continue? (yes/no): " answer
    case $answer in
        [Yy]* ) echo "Proceeding with the operation..." ;;
        [Nn]* ) echo "Operation canceled."; exit 0 ;;
        * ) echo "Please answer yes or no."; confirm_action "$1";;
    esac
}

read -p "Enter the environment you wish to restore (dev, val, eph-*): " ENV

if [[ $ENV == *"prod"* ]]; then
    confirm_action "Warning: This script is not intended for production. Are you sure you want to proceed?"
fi

read -p "Enter the path to the backup file you want to restore: " RESTORE_FILE
if [ ! -f "$RESTORE_FILE" ]; then
    echo "Backup file not found! Please check the path and try again."
    exit 1
fi

LAMBDA_FUNCTION_NAME="cms-eregs-$ENV-regsite"

# Get the environment variables from the Lambda function
data=$(aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --query 'Environment.Variables.{DB_HOST:DB_HOST,DB_PORT:DB_PORT,DB_NAME:DB_NAME,DB_SECRET:DB_SECRET}' --output text)
data_array=($data)
DB_HOST=${data_array[0]}
DB_NAME=${data_array[1]}
DB_PORT=${data_array[2]}
DB_SECRET=${data_array[3]}

# Get the database user and password from the Lambda function
data=$(aws secretsmanager get-secret-value --secret-id $DB_SECRET --query 'SecretString' --output text)
DB_USER=$(echo $data | jq -r '.username')
DB_PASSWORD=$(echo $data | jq -r '.password')

# Validate if the environment variables were parsed correctly
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  echo "Failed to retrieve necessary environment variables. Exiting..."
  exit 1
fi

if [[ $ENV == *"prod"* ]]; then
    # Backup the database that we are restoring.
    echo "Backing up $DB_NAME before restoring..."
    CURRENT_DATE=$(date +"%Y%m%d%H%M%S")
    BACKUP_FILENAME="${DB_HOST}_${DB_NAME}_${CURRENT_DATE}.sql"
    PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > $BACKUP_FILENAME
    echo "Database backed up successfully to {$BACKUP_FILENAME}"
fi

echo "Dropping database $DB_NAME on $DB_HOST now..."
# Drop existing database
# we use postgres as the database name as the given database is in use.
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME} WITH ( FORCE );"

echo "Creating new database..."
# Create new database
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -c "CREATE DATABASE ${DB_NAME};"

echo "Restoring data from backup file ${RESTORE_FILE}"
# Restore data from a backup file. (this is a different file than existing db backup file)
# restore the data with an existing backup file.
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d ${DB_NAME} < $RESTORE_FILE

echo "Database restore completed successfully."
