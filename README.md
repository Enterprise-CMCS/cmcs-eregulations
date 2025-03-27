# CMCS eRegulations

[![Deploy](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions/workflows/deploy.yml/badge.svg)](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions/workflows/deploy.yml)
[![Parser Tests](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions/workflows/lint-and-test-parsers.yml/badge.svg)](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions/workflows/lint-and-test-parsers.yml)
[![CodeQL](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Enterprise-CMCS/cmcs-eregulations/actions/workflows/github-code-scanning/codeql/)

# About

This is a project for the Center for Medicaid and CHIP Services (CMCS) to meet needs of staff researching regulations and related guidance, building on the [eRegulations](https://eregs.github.io/) open source project.

We have public documentation about our product, design, and research processes in [this repository wiki](https://github.com/Enterprise-CMCS/cmcs-eregulations/wiki).

# Local setup

## Prerequisites

You need these to get started:

-   git
-   Docker, including Docker Compose (install [Docker Desktop](https://docs.docker.com/desktop/))
-   Python 3.12 (consider using [Homebrew](https://docs.brew.sh/Homebrew-and-Python))
-   [Node](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) >= v20, which includes npm (we suggest using [nvm](https://github.com/nvm-sh/nvm))
-   [go](https://go.dev/dl/) version 1.16
-   **Prevent security incidents:** To stop yourself from accidentally pushing secrets to GitHub, you must set up pre-commit hooks in your local environment: [SECRETSCANNING.md](SECRETSCANNING.md#quick-start).


## Get the code

```
git clone https://github.com/Enterprise-CMCS/cmcs-eregulations
```

Or if using SSH keys:

```
git clone git@github.com:Enterprise-CMCS/cmcs-eregulations.git
```

## Create the Dockerfile

```
cd solution
cp Dockerfile.template Dockerfile
```

The Dockerfile has several environment variables. For local development, you can leave them blank to use default values.

## Run the application

To start a local Docker environment and load a few parts of 42 CFR and 45 CFR:

```
cd solution
make local
```

Create static assets to give the site the proper CSS files, including the admin panel:

```
cd solution
make local.collectstatic
```

Proceed to <http://localhost:8000> in your browser to see the results.

Run `make watch-all` to automatically compile your local changes to SCSS and JS so that you can see them in your browser.

Run `make local.createadmin` to create an admin superuser for the admin portion of the site. Proceed to <http://localhost:8000/admin> to access the admin portion and login with the credentials you created in the previous step.

You can run `make` to learn about other available tasks. For example:

`make local.seed` will load data from the fixtures folder, setting up some sample data for local use. This data is not maintained and should not be relied on for any purpose other than development.

`make local.stop` will cause the running Docker processes to stop without losing data.

`make local.clean` will remove the local environment completely, useful when you want to start fresh.

## Run tests

#### Testing setup

Before running the tests for the first time, you may need to install Cypress dependencies.

1. Navigate to project root
2. `cd solutions/ui/e2e`
3. `npm install`

> [!NOTE]
> If the Cypress install process fails or hangs for an unreasonably long time, refer to the ["Troubleshoot installation" section of the Cypress installation guide](https://docs.cypress.io/app/references/advanced-installation#Troubleshoot-installation) and follow the instructions for the npm package manager.

#### Running the tests

1. Navigate to project root
2. If project is not already running locally, run `make local`
3. For Cypress run `make test.cypress`. This will run our Cypress suite.
4. For Python unit tests, run `make test.pytest`. This will run our Python unittest using pytest.
5. For Vitest run `make test.vitest`.  This will run our Vitest suite.

## Run linters

#### ESLint

This project uses ESLint to enforce consistent coding styles across the frontend (JavaScript) and infrastructure (TypeScript) components, improving code readability and reducing the likelihood of runtime errors. We use a shared ESLint configuration (`eslint-global-rules.mjs` file) at the project root to define a baseline of rules applicable to both the frontend and infrastructure code. Each application (frontend and CDK) also maintains its own ESLint configuration file, to allow tailoring rules and plugins to JavaScript and TypeScript.

To run ESLint, execute the following commands from the project root:

```
make eslint-frontend

make eslint-cdk
```

For more information and resources to help integrate ESLint into your text editor, see [LINTING.md](solution/LINTING.md).

## Working with single-sign-on

To use our Okta identity provider locally, you need to update the OIDC_RP and OIDC_OP environment variables in your Dockerfile. See internal authentication developers guide.

# Deployment

See [CDK Readme](cdk-eregs/README.md).

To use our Okta identity provider on an experimental (ephemeral) deployment, see internal authentication developers guide.

# Development tips

## Export and import data

To update local data with the most recent version of production, you need access to the production database and pg_dump. You can also use these instructions to update dev or val data with fresh data from production.

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
7. Run the script by executing ./scripts/backup_db.sh from your terminal.
8. Once the backup process is finished, you'll find a copy of the backup file in the directory where the command was executed.

   - The file will be named in the following format: `<db host name>_<name of your db>_<date>.sql`.

9. With the backup file ready, proceed to restore the database by running the script `./scripts/restore_db.sh`.

   - local database name: `localhost`
   - local port: `5432`

10. Upon running the restoration script, you'll receive a prompt indicating that the existing database will be replaced. If you're certain, type yes.

11. Follow the subsequent prompts, providing the necessary credentials. When prompted for the backup file, enter the name of the file generated during the backup process.

12. Before the database is restored, a backup is created of the db that is being restored. The file will be named in the following format: `<db host name>_<name of your db>_<date>.sql`. 

   - Visit the local website and ensure that the data has been copied. 

## Add a new model

If adding a new model, update the following files:

- In populate_content.py add it to both the add it to the fixtures list.  First part of it is the JSON file, the other is the model.
- In the make file, either add it to the list of objects, or add a new line for the model.
- In the emptyseedtables.py add the model to the handler command.

## Update CSS for admin site

To change the styling of the admin site, add custom style rules to `solution/ui/regulations/css/admin/custom_admin.css`.  

To see the changes on the admin site, run `make local.collectstatic`.  This will update/create the CSS files in the `solution/static-assets/css/admin` directory.

You will need to restart the local environment to see the changes. The Makefile will automatically move those files to the correct location where `STATIC_ROOT` is defined. This is the location where Django will look for static files.

For admin site customizations, use the icon set at [Boxicons](https://boxicons.com).
