# About

This is part of a one-year pilot project for the Center for Medicaid and CHIP Services (CMCS) to understand and meet needs of CMCS and State staff researching regulations and related guidance, building on the [eRegulations](https://eregs.github.io/) open source project.

We have public documentation about our product, design, and research processes in [this repository wiki](https://github.com/CMSgov/cmcs-eregulations/wiki).

# Prerequisites
- Docker
- Docker Compose
- go version 1.16
- git
- node >= v15 (We suggest using [nvm](https://github.com/nvm-sh/nvm))

# Getting setup

**Getting the code**

```
git clone https://github.com/cmsgov/cmcs-eregulations
```

**Running eRegs:**
A lot of tasks for local development can be accessed through the Makefile.
Running `make` will provide some information about the available tasks.

For example:
```
make local
```
Will start a local docker environment and load parts of Title 42 into it.

Proceed to http://localhost:8000 in your browser to see the results.

To stop the local eRegs `make local.stop` will cause the running docker processes to stop without losing data.

While `make local.clean` will remove the local environment completely, useful when you want to start fresh.


**Testing eRegs:**
Running `make test` after `make local` will run the cypress suite of end to end tests.

**Working with assets:**
scss and js files can be watched an automatically compiled with `make watch`.