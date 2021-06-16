# About

This is part of a one-year pilot project for the Center for Medicaid and CHIP Services (CMCS) to understand and meet needs of CMCS and State staff researching regulations and related guidance, building on the [eRegulations](https://eregs.github.io/) open source project.

Our related repositories with forks of eRegs code: [regulations-core](https://github.com/CMSgov/regulations-core), [regulations-parser](https://github.com/CMSgov/regulations-parser), [regulations-site](https://github.com/CMSgov/regulations-site).

We have public documentation about our product, design, and research processes in [this repository wiki](https://github.com/CMSgov/cmcs-eregulations/wiki).

# Prerequisites
- Docker
- Docker Compose
- git
- node >= v15 (We suggest using [nvm](https://github.com/nvm-sh/nvm))

# Getting setup

**Getting the code**

```
git clone --recurse-submodules https://github.com/cmsgov/cmcs-eregulations
```

**Running eRegs:**
A lot of tasks for local development can be accessed through the Makefile.
Running `make` will provide some information about the available tasks.

For example:
```
make local
```
Will start a local docker environment and load Title 42 Parts 400 and 433 into it.

Proceed to http://localhost:8000 in your browser to see the results.

To stop the local eRegs `make local.stop` will cause the running docker processes to stop without losing data.

While `make local.clean` will remove the local environment completely, useful when you want to start fresh.
