# About

This is part of a one-year pilot project for the Center for Medicaid and CHIP Services (CMCS) to understand and meet needs of CMCS and State staff researching regulations and related guidance, building on the [eRegulations](https://eregs.github.io/) open source project.

Our related repositories with forks of eRegs code: [regulations-core](https://github.com/CMSgov/regulations-core), [regulations-parser](https://github.com/CMSgov/regulations-parser), [regulations-site](https://github.com/CMSgov/regulations-site).

# Prerequisites
- Docker
- Docker Compose
- git

# Getting setup

**Getting the code**

```
git clone --recurse-submodules https://github.com/cmsgov/cmcs-eregulations
```

**Run the script to start eRegs:**

```
./run.sh <api key>
```

**Visit eRegs locally:**
Proceed to http://localhost:8000 in your browser.

**Stopping eRegs**

```
docker-compose down
```

