# Policy Connector

[![Deploy](https://github.com/A1MSolutions/policyconnector/actions/workflows/deploy.yml/badge.svg)](https://github.com/A1MSolutions/policyconnector/actions/workflows/deploy.yml)
[![Parser Checks](https://github.com/A1MSolutions/policyconnector/actions/workflows/parser-checks.yml/badge.svg)](https://github.com/A1MSolutions/policyconnector/actions/workflows/parser-checks.yml)

# About

Policy Connector is a web application for researching government policy information, including regulations and related guidance.

This is an independent non-government adaptation of an open source codebase, [eRegulations](https://eregs.github.io/), that has had many contributors:

1. The Consumer Financial Protection Bureau developed the first version of eRegulations in 2013 and [released it as an open source project](https://www.acus.gov/article/cfpbs-eregulations-tool-promises-help-users-navigate-federal-regulations). See its current iteration at [CFPB Interactive Bureau Regulations](https://www.consumerfinance.gov/rules-policy/regulations/).
2. At the General Services Administration, [18F helped a few agencies adapt eRegulations for their needs](https://18f.gsa.gov/our-work/eregulations/), including the Bureau of Alcohol, Tobacco, Firearms, and Explosives: [ATF eRegulations](https://regulations.atf.gov/) ([archived repository](https://github.com/18F/atf-eregs)).
3. The Center for Medicare & Medicaid Services reused eRegulations and developed additional features. This version is based on [the CMS codebase](https://github.com/Enterprise-CMCS/cmcs-eregulations).

# Getting set up

## Prerequisites

-   Docker
-   Docker Compose
-   go version 1.16
-   git
-   node >= v18 (We suggest using [nvm](https://github.com/nvm-sh/nvm))
-   pre-commit hooks
-   PostgreSQL 15

### Set up Git pre-commit hooks

See "Quick Start" in [SECRETSCANNING.md](SECRETSCANNING.md#quick-start) to ensure that pre-commit hooks are installed and working properly.

## Get the code

```
git clone https://github.com/A1MSolutions/policyconnector
```

Or if using SSH keys:

```
git clone git@github.com:A1MSolutions/policyconnector.git
```

## Create your Dockerfile

- Create the Dockerfile

```
cd solution
cp Dockerfile.template Dockerfile
```

- Update the Dockerfile with correct environment variables values

## Running

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

Will start a local Docker environment and load parts of Title 42 into it.

Proceed to <http://localhost:8000> in your browser to see the results.

`make local.createadmin` will create an admin superuser for the admin portion of the site.

Proceed to <http://localhost:8000/admin> to access the admin portion and login with the credentials you created in the previous step.

`make local.seed` will load data from the fixtures folder setting up a usable amount of data for local use.  
This data is not maintained and should not be relied on for any purpose other than development.

`make local.stop` will cause the running Docker processes to stop without losing data.

`make local.clean` will remove the local environment completely, useful when you want to start fresh.

## Update CSS for admin site

To change the styling of the admin site, add custom style rules to `solution/ui/regulations/css/admin/custom_admin.css`.  

To see the changes on the admin site, run `make local.collectstatic`.  This will update/create the CSS files in the `solution/static-assets/css/admin` directory.

You will need to restart the local environment to see the changes. The Makefile will automatically move those files to the correct location where `STATIC_ROOT` is defined. This is the location where Django will look for static files.

## Testing

#### Testing setup

Before running the tests for the first time, you may need to install Cypress dependencies.

1. Navigate to project root
2. `cd solutions/ui/e2e`
3. `npm install`

#### Running the tests

1. Navigate to project root
2. If project is not already running locally, run `make local`
3. For Cypress run `make test.cypress`. This will run our Cypress suite.
4. For Python unit tests, run `make test.pytest`. This will run our Python unittest using pytest.
5. For Vitest run `make test.vitest`.  This will run our Vitest suite.

## Linting and Formatting

#### ESLint

This project utilizes ESLint to maintain high code quality and enforce consistent coding styles across both the frontend (JavaScript) and infrastructure (TypeScript) components.  ESLint helps identify potential issues early, improving code readability and reducing the likelihood of runtime errors.

We leverage a shared ESLint configuration (`eslint-global-rules.mjs` file) at the project root to define a baseline of rules applicable to both the frontend and infrastructure code. This promotes consistency in fundamental coding practices across the entire project.

Each application (frontend and CDK) also maintains its own dedicated ESLint configuration file. This allows us to tailor rules and plugins specifically to the nuances of JavaScript and TypeScript, respectively, while still adhering to the core shared principles.  This approach ensures that each part of the project benefits from the appropriate linting rules for its language and context.

To run ESLint, execute the following commands from the project root:

```
// lint the frontend JS
make eslint-frontend

// lint CDK TS
make eslint-cdk
```

For more information on ESLint, as well as resources to help integrate ESLint into your text editor, see [LINTING.md](solution/LINTING.md).

## Working with assets

Navigate to project root.

`make watch-all`: SCSS and JS files can be watched and automatically compiled.

For admin site customizations, please use the icon set at [Boxicons](https://boxicons.com).

## Importing resource data

See the [Exporting data from production](#exporting-data-from-production) section of the README below to get a copy of the data.

## Exporting data from production

If the data seems out of sync with production, you may want to get a more recent version of the data from production.

In order to update your local data with the most recent version of production, you will need to have access to our production database, pg_dump, and access to the CMS VPN.

1. You must have the correct version of PostgreSQL installed locally on your machine (see [prerequisites](#prerequisites) for version number). Local PostgreSQL server must be turned **off**.
2. Ensure you have [AWS CLI](#https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed locally on your machine.
3. Connect to the VPN. 
4. Create a backup of the database you intend to restore using pg_dump. Execute the following command:

   - `pg_dump -U <DB_USER> -h <DB_HOST> -p <DB_PORT> <DB_NAME> > <name_you_want_your_backupfile_to_be>`
   - It is recommended that you put these backups in a folder that is hidden from `git`.  We suggest creating a folder in the root of the project named `db_backup` and dumping all of your backups into it.  This directory name is safe to use, as it has already been added to the project's `.gitignore`.

> [!NOTE]
> restore_db.sh also performs a backup of the database you intend to restore. However, as a precautionary measure, it's advisable to create a separate backup of your database.)
5. Sign in to the Cloudtamer CMS portal (cloudtamer.cms.gov) to retrieve your short-term access keys.
6. Paste the access keys into your terminal. This will enable you to use AWS CLI commands.
7. Run the script by executing ./solution/backend/scripts/backup_db.sh from your terminal.
8. Once the backup process is finished, you'll find a copy of the backup file in the directory where the command was executed.

   - The file will be named in the following format: `<db host name>_<name of your db>_<date>.sql`.

9. With the backup file ready, proceed to restore the database by running the script `./solution/backend/scripts/restore_db.sh`.

   - local database name: `localhost`
   - local port: `5432`

10. Upon running the restoration script, you'll receive a prompt indicating that the existing database will be replaced. If you're certain, type yes.

11. Follow the subsequent prompts, providing the necessary credentials. When prompted for the backup file, enter the name of the file generated during the backup process.

12. Before the database is restored, a backup is created of the db that is being restored. The file will be named in the following format: `<db host name>_<name of your db>_<date>.sql`. 

   - Visit the local website and ensure that the data has been copied. 


## Adding a new model

If adding a new model, update the following files:

- In populate_content.py add it to both the add it to the fixtures list.  First part of it is the JSON file, the other is the model.
- In the make file, either add it to the list of objects, or add a new line for the model.
- In the emptyseedtables.py add the model to the handler command.
