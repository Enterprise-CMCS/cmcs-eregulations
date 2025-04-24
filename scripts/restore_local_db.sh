#!/bin/bash
set -e

read -p "Enter the path to the backup file you want to restore: " RESTORE_FILE
if [ ! -f "$RESTORE_FILE" ]; then
    echo "Backup file not found! Please check the path and try again."
    exit 1
fi

DB_HOST=localhost
DB_NAME=eregs
DB_USER=eregsuser
DB_PORT=5432
read -p "Enter the database password: " DB_PASSWORD

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
