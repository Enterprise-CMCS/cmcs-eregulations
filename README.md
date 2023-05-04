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

# Getting setup

## Getting the code

```
git clone https://github.com/Enterprise-CMCS/cmcs-eregulations
```
## Create your Dockerfile

- Create the dockerfile

```
cd solution
cp DockerFile.template DockerFile
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

Running `make test` after `make local` will run the cypress suite of end to end tests.

1. Navigate to project root
2. If project is not already running locally, run `make local`
3. `make test`

## Working with assets

Navigate to project root.
`make watch-all`: SCSS and JS files can be watched an automatically compiled.
For admin site customizations, please use the icon set at [boxicon](https://boxicons.com).

## Exporting data from Production

Every type of model has an "Export to JSON" button that will export the data to a JSON format that can be easily imported
by saving the file to the fixtures folder and importing it with the built in `loaddata` command from Django.

## Running eRegs Prototype

To better support Rapid Prototyping, a VueJS Single Page Application (SPA) has been created using the [Vue CLI](https://cli.vuejs.org/).

1. `make prototype` to spin up Docker container
2. visit `localhost:8081` to view prototype
3. edit files in `/regulations/static/prototype` to make changes
4. changes should be reflected in running prototype via hot reloading
5. `make prototype:clean` to tear down Docker container
