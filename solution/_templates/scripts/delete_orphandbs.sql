-- find all the databases.  Script must be run connected to the database
select datname from pg_database;
-- drop the database(do it one at a time, let not be wreckless here)
drop database if exist --dbname;