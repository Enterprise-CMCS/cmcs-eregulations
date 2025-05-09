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
> If the Cypress install process fails or hangs for an unreasonably long time, refer to the ["Troubleshoot installation" section of the Cypress installation guide](https://docs.cypress.io/app/references/advanced-installation#Troubleshoot-installation) and follow the instructions for the npm package manager.  Instead of running `npm install`, run the following commands:

```
CYPRESS_INSTALL_BINARY=0 npm install cypress --save-dev
DEBUG=cypress:cli* npx cypress install
```

#### Running the tests

1. Navigate to project root
2. If project is not already running locally, run `make local`
3. For Cypress run `make test.cypress`. This will run our Cypress suite.
4. For Python unit tests, run `make test.pytest`. This will run our Python unittest using pytest.
5. For Vitest run `make test.vitest`.  This will run our Vitest suite.

## Run linters

#### ESLint

This project uses ESLint to enforce consistent coding styles across the frontend (JavaScript) and infrastructure (TypeScript) components, improving code readability and reducing the likelihood of runtime errors. We use a shared ESLint configuration file located at the root of the project.  This file is used by all JavaScript and TypeScript files in the project, including all CDK TS files, Cypress end to end test suites and config files, and all front end files including Vue components and related Javascript files.

To run ESLint, execute the following command from `./solution`:

```
make eslint
```

For more information and resources to help integrate ESLint into your text editor, see [LINTING.md](solution/LINTING.md).

## Working with single-sign-on

To use our Okta identity provider locally, you need to update the OIDC_RP and OIDC_OP environment variables in your Dockerfile. See internal authentication developers guide.

# Deployment

See [CDK Readme](cdk-eregs/README.md).

To use our Okta identity provider on an experimental (ephemeral) deployment, see internal authentication developers guide.

# Development tips

## Backing up and restoring the database

The scripts `backup_db.sh`, `restore_remote_db.sh`, and `restore_local_db.sh` can be used for the following purposes:

* Copying the prod DB to dev and val for more accurate testing.
* Copying an RDS database to your local environment.
* Restoring one or more databases from a previously taken backup without using RDS Snapshots.

You must have the correct version of PostgreSQL installed locally on your machine (see [prerequisites](#prerequisites) for version number). To prevent connection conflicts, the local PostgreSQL server must be turned **off**. You also need the AWS CLI installed and configured with your short-term access keys from Cloudtamer. Additionally, be sure to run `export AWS_REGION=<your region>`. To access RDS and Cloudtamer, you must be connected to the VPN.

### Creating a backup

1. Run `mkdir -p db_backup; cd db_backup` from the eRegs root directory. This creates a `db_backup` directory which is already hidden from Git.
2. Run `../scripts/backup_db.sh` to start the backup process.
3. Specify the environment you wish to backup. (`dev`, `val`, `prod`, etc.)
4. Wait for the script to fetch the database parameters and perform the backup.

When done, the backup file will be named `<DB host>_<name of DB>_<date>.sql`.

### Restoring from a backup file to RDS

1. From the `db_backup` directory, run `../scripts/restore_remote_db.sh`.
2. Enter the relative path to the SQL backup file created above.
3. Specify the environment you wish to restore. (`dev`, `val`, `prod`, `eph-*`, etc.)
4. Wait for the script to fetch the database parameters, create a backup of the remote DB, and perform the restore. This will take a while.

Note that specifying `prod` as an environment will prompt for confirmation. Be absolutely sure that the backup that you have taken is valid and the file you specify is the correct one. However, this script will take a backup of the remote DB first before restoring from the specified file. If an error occurs, this new backup can be used for recovery. If this fails, a restore from an RDS Snapshot will be required.

### Restoring from a backup file to local PostgreSQL

1. From the `db_backup` directory, run `../scripts/restore_local_db.sh`.
2. Enter the relative path to the SQL backup file created above.
3. Enter the password to the local database.
4. Wait for the script to restore the local database from the file. This may take a few minutes.d

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

## Deleting old CloudFormation stacks
Sometimes, the `remove-experimental.yml` Github Action fails to complete, leaving some resources left in AWS. Over time these resources can built up and become a nuisance.

We have 2 scripts in our repo that can assist with cleaning up unused stacks and resources. Both are contained in the `./scripts` directory. Both scripts require the `boto3` library to be installed on your machine, and an AWS account must be configured either via CLI profile or environment variables. Be sure to run `export AWS_REGION=<your_region>` as well.

On most systems, installing `boto3` is as simple as running `pip install boto3` or `pip3 install boto3` assuming you have both Python3 and Pip (or Pip3) installed. On MacOS systems where Python and Pip are installed with Homebrew, you may need to create a Python virtualenv first:

```bash
$ python3 -m venv /path/to/new/venv_directory
$ source /path/to/new/venv_directory/bin/activate
$ pip3 install boto3
$ ./run/scripts/below
```

### delete_stacks.py

This script will retrieve a list of all experimental deployments and automatically delete them in parallel using a thread pool. The thread pool's size is proportional to the size of your terminal window to allow you to easily track the progress.

**Example:**
To delete all experimental deployments _except_ the stacks belonging to PR numbers 1234 and 6789, run `./scripts/delete_stacks.py --exclude-prs 1234 6789`.

**Example:**
To perform a dry run of the delete action, run `./scripts/delete_stacks.py --dry-run`. The dry run will also simulate a short delay between deleting resources. This makes the dry run more realistic, as well as pevents contention between the various threads in the thread pool.

### delete_resources.py

This script retrieves a list of all S3 Buckets, Security Groups, and Log Groups that belong to an experimental deployment but are not associated with any CloudFormation stack that exists currently.

The script runs in three steps, one for each resource type, and prompts the user to delete the listed resources or not. If the user selects no, it will move on to the next resource type.

This does not run in parallel to better display error messages and give the user a chance to respond to issues, however it is usually very fast compared to deleting stacks so this is not a concern.

To use this script, just run `./scripts/delete_resources.py` with no arguments needed.
