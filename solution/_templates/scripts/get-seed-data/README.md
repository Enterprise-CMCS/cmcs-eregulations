# About

This section is about how to update our dev environment data with that of production.  This pertains only to our supplmental content, federal register documents, and synonyms.  Our regulations data is populated using the parser.

# Prerequisites

-   The ability to connect to our vpn
-   The database connection address and port number
-   A running docker container of our database
-   pg_dump, you can set this up in linux, windows, or mac.

The pg_dump command will pull in all of resources app in djangos tables as well as the synonym tables in the search app.  It pulls it in as a sql command inesert into column.  It will pull in some pg_audit stuff at the end that will cause an error but the rest of it will run fine and updates the tables as expected.  The next part is to clear out the resources tables and the synonym table which is done by an additional script.  The final step is to run the sql file created by pg_dump.

# Getting setup

## Getting the data
First run the pg_dump command below in commandline.  It will produce a file called backup.sql in the folder you run the command in.  You will need to update the command to have the proper database endpoint and the port number.

```
pg_dump -h <db_address> -p <port_number> -U eregsuser -f backup.sql -t 'search_sy*' -t 'resources_*' --data-only --column-inserts eregs
```

After you enter it, you will be prompted for the database password.

## Disconnect from the production database.

IMPORTANT! Disconnect from the production database.  Do not do any further steps until you do so since it might cause issues in production.  To play it safe also disconnect from your VPN.

## Upating your local database.

1. Connect to your local database instancce
2. Run the sql script "clear-tables.sql" located in this directory.  This removes data from the tables to be updated.
3. Run the newly created "backup.sql" file created from the pg_dump command you ran earlier. Note: Towards the end of the script there are some pg_audit items that will fail on the sql job.  You can ignore the failures or remove them from the sql file.

## Updating the seed data

1. Run the make command in the solution directory ```make local.dump```.  This will produce json files for our resources app and the synonyms.
2. Push a PR with the newly updated json files.
3. Check the dev branch created by the experimental deploy after it is finished building.  Resources should be up to date.
