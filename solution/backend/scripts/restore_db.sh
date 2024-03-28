#!/bin/bash
set -e
# This script deletes the database and then restores it from backup.
# Before running this script make a backup of the data you want to restore with pg_dump.
# This script does make a backup of the data it's restoring but its recommended to backup that data as well.
# you can also use backup_db.sh to do the backup. Once you have the backup file run this script

# Function to display error messages and exit
error_exit() {
    echo "Error: $1"
    exit 1
}

# Function to display warning message and get user confirmation
confirm_action() {
    read -p "$1 Do you wish to continue? (yes/no): " answer
    case $answer in
        [Yy]* ) echo "Proceeding with the operation..." ;;
        [Nn]* ) echo "Operation canceled."; exit 0 ;;
        * ) echo "Please answer yes or no."; confirm_action "$1";;
    esac
}

confirm_action "Warning: This script will delete the postgres database in order to restore it."

# Prompt for user input
read -p "Enter the database user: " DB_USER
read -p "Enter the database host: " DB_HOST
read -p "Enter the database port: " DB_PORT
read -p "Enter the database name: " DB_NAME
read -p "Enter the path to the backup file: " BACKUP_FILE
read -sp "Enter the database password: " DB_PASSWORD


# Backup the database that we are restoring.
echo "Starting database backup for $DB_NAME ..."

CURRENT_DATE=$(date +"%Y%m%d%H%M%S")
BACKUP_FILENAME="${DB_NAME}_${CURRENT_DATE}.sql"
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > $BACKUP_FILENAME
echo "Database backed up successfully to {$BACKUP_FILENAME}"

echo "Dropping database postgres"
# Drop existing database
# we use postgres as the database name as the given database is in use.
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -c "DROP DATABASE IF EXISTS eregs WITH ( FORCE );"

echo "Creating new database..."
# Create new database
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -c "CREATE DATABASE eregs;"

echo "Restoring data from backup file ${BACKUP_FILE}"
# Restore data from a backup file. (this is a different file than existing db backup file)
# restore the data with an existing backup file.
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d eregs < $BACKUP_FILE
echo "Database restore completed successfully."
