#!/bin/bash
# This script will dump the given database data to a file.
# Prompt for user input
read -p "Enter the database user: " DB_USER
read -p "Enter the database host: " DB_HOST
read -p "Enter the database port: " DB_PORT
read -p "Enter the database name: " DB_NAME
read -sp "Enter the database password: " DB_PASSWORD

CURRENT_DATE=$(date +"%Y%m%d%H%M%S")
BACKUP_FILENAME="${DB_HOST}_${DB_NAME}_${CURRENT_DATE}.sql"

PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h $DB_HOST -p $DB_PORT $DB_NAME > $BACKUP_FILENAME
