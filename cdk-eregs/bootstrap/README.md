# Update Template Script

## Overview

In order for our CDK scripts to reliably deploy/create AWS resources, we need to keep our CDK stacks up to date.

We decided to do this via a GitHub Action, but found it wasn't possible using standard bootstrap procedure because we rely on a CMS-specific `template.yaml`.  By diffing the CMS `template.yaml` with the [default one from CDK](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk/lib/api/bootstrap/bootstrap-template.yaml), we found it was feasible to create a script (`update_template.py`) that attempts to automatically apply those needed changes to the default template.

From there, we can automate the bootstrap update procedure. We decided to run this update periodically on request, instead of automatically on a recurring schedule, to make it easier to check for any breaking changes or other impacts to our deployment process.

## Prerequisites

- Python 3.x
- Required Python packages (listed in `requirements.txt`)
- A copy of the [default template.yaml from CDK](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk/lib/api/bootstrap/bootstrap-template.yaml)
- A role to assume (for eRegs it is `ct-ado-eregs-application-admin`, for example)

## Setup

First, download the default `template.yaml`. Then, create a file called `roles.json`. This file contains a list of dictionaries like so:

```jsonc
[
    {
        "name": "FilePublishingRole",
        "nested_policy": false,
        "update_policy": true
    },
    ....... more roles .......
]
```

Where `name` is the name of the role to update, `nested_policy` is a boolean indicating whether the policy document to update is nested in an Fn::If block, and `update_policy` specifies whether to attempt to update the policy document at all.

Note that if a role is specified in the list, regardless of the status of the `update_policy` boolean, the script will _always_ add a role path and permissions boundary. This boolean only tells the script if it should _also_ update the `AssumeRolePolicyDocument` block of the YAML for that role.

## Usage

To run the `update_template.py` script, use the following command:
```sh
./update_template.py <role file> <input template> <output filename> <name of role to assume>
```
Where `role file` is the filename of the `roles.json` you created earlier, `input template` is the default CDK template.yaml file, `output filename` is the filename to write the updated template to, and `name of role to assume` is the role unique to your project.

## Additional options

In addition to the four positional arguments that `update_template.yaml` takes, you can also specify the following: 

`--boundary-policy-arn-prefix BOUNDARY_POLICY_ARN_PREFIX`<br/>
ARN prefix of the permissions boundary policy to attach to the roles. Default is: `arn:${AWS::Partition}:iam::${AWS::AccountId}:policy/`.

`--boundary-policy-name BOUNDARY_POLICY_NAME`<br/>
Name of the permissions boundary policy to attach to the roles. Default is: `cms-cloud-admin/ct-ado-poweruser-permissions-boundary-policy`.

`--role-to-assume-arn-prefix ROLE_TO_ASSUME_ARN_PREFIX`<br/>
ARN prefix of the role to be added to the AssumeRolePolicyDocument. Default is: `arn:aws:iam::${AWS::AccountId}:role/`.

`--role-path ROLE_PATH`<br/>
Path to be added to the role properties. Default is: `/delegatedadmin/developer/`.

## Automating CDK updates via Github Actions

See our GitHub Actions script here: [/.github/workflows/update-cdk-bootstrap.yml](/.github/workflows/update-cdk-bootstrap.yml)
