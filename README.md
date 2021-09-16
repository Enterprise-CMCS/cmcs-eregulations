# About

This is a project for the Center for Medicaid and CHIP Services (CMCS) to meet needs of CMCS and State staff researching regulations and related guidance, building on the [eRegulations](https://eregs.github.io/) open source project.

We have public documentation about our product, design, and research processes in [this repository wiki](https://github.com/CMSgov/cmcs-eregulations/wiki).

# Prerequisites

- Docker
- Docker Compose
- go version 1.16
- git
- node >= v15 (We suggest using [nvm](https://github.com/nvm-sh/nvm))

# Getting setup

## Getting the code ##

```
git clone https://github.com/cmsgov/cmcs-eregulations
```

## Running eRegs ##

A lot of tasks for local development can be accessed through the Makefile.
Running `make` will provide some information about the available tasks.

For example:

```
make local
```

Will start a local docker environment and load parts of Title 42 into it.

Proceed to <http://localhost:8000> in your browser to see the results.

`make local.stop` will cause the running docker processes to stop without losing data.

`make local.clean` will remove the local environment completely, useful when you want to start fresh.

## Testing eRegs ##

#### Testing Setup ####

Before running the tests for the first time, you may need to install cypress dependencies.

1. `cd e2e`
2. `npm install`

#### Running the tests ####

Running `make test` after `make local` will run the cypress suite of end to end tests.

1. Navigate to project root
2. If project is not already running locally, run `make local`
3. `make test`

## Working with assets ##

`make watch`: scss and js files can be watched an automatically compiled
