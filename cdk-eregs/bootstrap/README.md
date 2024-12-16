# Update Template Script

## Overview

In order for our CDK scripts to reliably deploy/create AWS resources, we need to keep our CDK stacks up to date.

We decided we wanted to do this automatically via cron'd Github Action, but found it wasn't possible to do this using standard bootstrap procedure because we are relying on a CMS-specific `template.yaml`.  By diffing the CMS `template.yaml` with the [default one from CDK](https://github.com/aws/aws-cdk/blob/main/packages/aws-cdk/lib/api/bootstrap/bootstrap-template.yaml), we found it was feasible to create a script (`update_template.py`) that attempts to automatically apply those needed changes to the default template.

From there, we can automate the bootstrap update procedure.

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

This sample script should provide the starting point for a script that can automatically update the CDK bootstrap:

```yaml
name: Update CDK Bootstrap

on:
  schedule:
    - cron: '0 0 * * 1' # Runs every Monday 

permissions:
  id-token: write
  contents: read
  actions: read

jobs:
  update-cdk-bootstrap:
    strategy:
      max-parallel: 1
      matrix:
        environment: ["dev", "val", "prod"]

    runs-on: ubuntu-latest

    environment:
      name: ${{ matrix.environment }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Configure AWS credentials for GitHub Actions
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_OIDC_ROLE_TO_ASSUME }}
          aws-region: us-east-1

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18.14

      - name: Install AWS CDK
        run: npm install -g aws-cdk # Install CDK

      - name: Update CDK Bootstrap
        env:
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }} # Get the account ID and region
          AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION }}
        run: |
          pushd cdk-eregs/bootstrap

          # Use curl to download the latest template.yaml directly from the CDK repo
          curl -s "https://raw.githubusercontent.com/aws/aws-cdk/refs/heads/main/packages/aws-cdk/lib/api/bootstrap/bootstrap-template.yaml" -o latest-template.yaml > /dev/null

          # Install script requirements
          pip install -r requirements.txt

          # Use update_template.py to generate our custom template.yaml
          # Note the role-to-assume name of 'ct-ado-eregs-application-admin',
          # update this for your use-case.
          ./update_template.py roles.json latest-template.yaml template.yaml ct-ado-eregs-application-admin

          # Create a temporary CDK app for bootstrapping purposes only
          mkdir temp; pushd temp
          cdk init app --language=typescript > /dev/null

          # Copy the default template into the new CDK app
          cp ../template.yaml .

          # Run cdk bootstrap with the custom template
          # Note other account-specific parameters that can be adjusted for your use-case
          cdk bootstrap --template template.yaml \
            --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess,arn:aws:iam::${AWS_ACCOUNT_ID}:policy/ADO-Restriction-Policy,arn:aws:iam::${AWS_ACCOUNT_ID}:policy/CMSApprovedAWSServices \
            --custom-permissions-boundary ct-ado-poweruser-permissions-boundary-policy \
            --qualifier one

          popd; popd
```
