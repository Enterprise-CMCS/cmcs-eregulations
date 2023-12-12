# About

[![Actions Status](https://github.com/Enterprise-CMCS/cmcs-eregulations/workflows/eCFR%20Parser%20Checks/badge.svg)](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions)

This is a project for the Center for Medicaid and CHIP Services (CMCS) to meet needs of CMCS and State staff researching regulations and related guidance, building on the [eRegulations](https://eregs.github.io/) open source project.

We have public documentation about our product, design, and research processes in [this repository wiki](https://github.com/Enterprise-CMCS/cmcs-eregulations/wiki).

# Prerequisites

-   Docker
-   Docker Compose
-   go version 1.16
-   git
-   node >= v18 (We suggest using [nvm](https://github.com/nvm-sh/nvm))
-   pre-commit hooks

# Getting setup

## Set Up Git pre-commit hooks

See "Quick Start" in [SECRETSCANNING.md](SECRETSCANNING.md#quick-start) to ensure that pre-commit hooks are installed and working properly.

## Getting the code

```
git clone https://github.com/Enterprise-CMCS/cmcs-eregulations
```

## Create your Dockerfile

- Create the dockerfile

```
cd solution
cp Dockerfile.template Dockerfile
```

- Update the dockerfile with correct environment variables values

## Running eRegs

A lot of tasks for local development can be accessed through the Makefile.
Running `make` will provide some information about the available tasks.

For example:

```
cd solution
make local
```

## Create static assets

Running this will create all the static assets so that the admin page
has the proper CSS files to display properly.

```
cd solution
make local.collectstatic
```

Will start a local docker environment and load parts of Title 42 into it.

Proceed to <http://localhost:8000> in your browser to see the results.

`make local.createadmin` will create an admin superuser for the admin portion of the site.

Proceed to <http://localhost:8000/admin> to access the admin portion and login with the credentials you created in the previous step

`make local.seed` will load data from the fixtures folder setting up a usable amount of data for local use.  
This data is not maintained and should not be relied on for any purpose other than development.

`make local.stop` will cause the running docker processes to stop without losing data.

`make local.clean` will remove the local environment completely, useful when you want to start fresh.

## Testing eRegs

#### Testing Setup

Before running the tests for the first time, you may need to install cypress dependencies.

1. Navigate to project root
2. `cd solutions/ui/e2e`
3. `npm install`

#### Running the tests

1. Navigate to project root
2. If project is not already running locally, run `make local`
3. For cypress run `make test.cypress`. This will run our cypress suite.
4. For python unit tests, run `make test.pytest`. This will run our python unittest using pytest.
5. For vitest run `make test.vitest`.  This will run our vitest suite.

## Working with assets

Navigate to project root.
`make watch-all`: SCSS and JS files can be watched an automatically compiled.
For admin site customizations, please use the icon set at [boxicon](https://boxicons.com).

## Importing resource data

To populate the created database with seed data for resources run the command below in the solution directory.

```
make local.seed
```

## Exporting data from Production

If the data is seemingly out of sync with production you may want to get a more recent version of the data from production.

In order to update your local data with the most recent version of production you will need to have access to our production database, pg_dump, and access to the cms.gov vpn.

If adding a new model to this process please refer to the adding a new model process below.

1.  Connect to the VPN and run the following command below for postgresql in the command line.  Replace db_address and port_number with the database address and port number respectively.  A file called `backup.sql` should populate in the directory the command is run in.
  - Django bases the tables off of ApplicationName_model.  So whenever resources_* will pul in all resourcces tables from postgres.  If you need to add a new model just follow the naming convention.
```
pg_dump -h <db_address> -p <port_number> -U eregsuser -f backup.sql -t 'search_sy*' -t 'resources_*' -t 'regulations_*' -t 'file_manager_subject' -t 'file_manager_documenttype' -t 'auth_g*' -t 'auth_permission' -t 'django_content_type' --data-only --column-inserts eregs
```
2. Run the command `make python.emptyseedtables`.  This will clear out many of our resources tables and the synonym table for population of the database.
3. Run the postges script `backup.sql` produced in step 2 on your local database.  This will update your database with up to date production data. 
    - Make sure you are running this on  your local database and not production.
    - There will be a couple errors for field not found towards the end of the sql script.  This is because of some fields added by pg_audit.  You can ignore it.
4.  Go into admin and verify the values were updated.  You should see things like supplemental content, federal register documents, sections, subparts, categories, fr_grouping, and synonyms are populated.
5.  Run the make command `make local.dump`.  This will overwrite the fixture files in the solution with the data now uploaded onto your machine. 
6.  Push the PR.  Your dev branch should be now using the proper fixture data.

### Adding a new model
1.  If adding a new model update the following files to do so.
    - In populate_content.py add it to both the add it to the fixtures list.  1st part of it is the json file, the other is the model
    - In the make file, either add it to the list of objects, or add a new line for the model.
    - In the emptyseedtables.py add the model to the handler command.

## Setting local to use EUA
1. Update your Dockerfile with the following environment variables
```
ENV OIDC_RP_CLIENT_ID=<your client id>
ENV OIDC_RP_CLIENT_SECRET=<your client secret>
ENV OIDC_OP_AUTHORIZATION_ENDPOINT=<authorization endpoint>
ENV OIDC_OP_TOKEN_ENDPOINT=<token endpoint>
ENV OIDC_OP_USER_ENDPOINT=<user endpoint>
ENV OIDC_OP_JWKS_ENDPOINT=<jwks endpoint>
ENV EUA_FEATUREFLAG=<set to 'true' if you want to see the eua link on admin login page>
```
These values can be found on AWS Parameter store.

## Register to test idp idm
- Sign into the URL [https://test.idp.idm.cms.gov/](https://test.idp.idm.cms.gov/) to access the CMS IDP (Identity Provider) portal.
- Set up Multi-Factor Authentication (MFA) for your account. Follow the provided prompts and instructions to complete the MFA setup process.
- Once your account has been successfully set up with MFA, please notify the CMS Okta team.
- Inform the CMS Okta team that you need to be added to the eRegs group.

Please note that the provided URL (https://test.idp.idm.cms.gov/) may require a valid CMS IDP account to access.

## Trouble shooting tips
- Issue: Setting OIDC_OP_AUTHORIZATION_ENDPOINT not found
  This error indicates that the environment variables are not properly set.
- Solution:
  - On your local environment verify that the DJANGO_SETTINGS_MODULE environment variable is set to ${DJANGO_SETTINGS_MODULE:-cmcs_regulations.settings.euasettings}. You can modify your docker-compose.yml file to include this setting: DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-cmcs_regulations.settings.euasettings}.
  - On dev,val,prod ensure that DJANGO_SETTINGS_MODULE is set correctly in AWS Param Store. 

## Serverless set up.
We use serverless in conjunction with github actions to deploy our application to our various environments.

### Functions
To allow us to deploy our application to various environments and prohibit certain lambda functions to be deployed to different environments we split our lambda functions out into a specific folder.  In backend/serverless_functions there is a different YMl file for each environment.  When you want to add a lambda function to each environment just add the function the corresponding environments folder.
