#!/usr/bin/env python3

import sys
import yaml
import json
import argparse


# Default values for the permissions boundary policy, role to assume, and role path
BOUNDARY_POLICY_ARN = "arn:${AWS::Partition}:iam::${AWS::AccountId}:policy/cms-cloud-admin/"\
                      "ct-ado-poweruser-permissions-boundary-policy"
ROLE_TO_ASSUME_ARN = "arn:aws:iam::${AWS::AccountId}:role/ct-ado-eregs-application-admin"
ROLE_PATH = "/delegatedadmin/developer/"


# Update the role properties to add the correct path and permissions boundary
def update_role_properties(properties: dict):
    properties["Path"] = ROLE_PATH
    properties["PermissionsBoundary"] = {
        "Fn::Sub": BOUNDARY_POLICY_ARN,
    }
    return properties


# Check if the statement matches the expected format for adding the role
def statement_matches(statement: dict):
    return all([
        statement.get("Action") == "sts:AssumeRole",
        statement.get("Effect") == "Allow",
        "Principal" in statement,
        type(statement["Principal"]) is dict,
        "AWS" in statement["Principal"],
    ])


# Update the principal to add the correct role
def update_principal(principal: dict):
    return {"AWS": [
        principal["AWS"],
        {"Fn::Sub": ROLE_TO_ASSUME_ARN},
    ]}


# Update the policy document statements to add the correct role as a principal in the correct place
def update_policy_doc_statements(yaml_statements: type[list | dict], nested: bool):
    statements = [yaml_statements] if type(yaml_statements) is not list else yaml_statements
    for i in statements:
        if nested and i.get("Fn::If"):
            ifs = [i["Fn::If"]] if type(i["Fn::If"]) is not list else i["Fn::If"]
            for j in [statement for statement in ifs if type(statement) is dict]:
                if statement_matches(j):
                    j["Principal"] = update_principal(j["Principal"])
                    return statements
        elif not nested and statement_matches(i):
            i["Principal"] = update_principal(i["Principal"])
            return statements
    return yaml_statements


# Process the role data to update the role properties and policy document statements
def process_role(role: dict, data: dict):
    try:
        data["Properties"] = update_role_properties(data["Properties"])
    except Exception as e:
        print(f'Error updating role properties for {role["name"]}: {e}')
        sys.exit(1)

    if role["update_policy"]:
        try:
            data["Properties"]["AssumeRolePolicyDocument"]["Statement"] = update_policy_doc_statements(
                data["Properties"]["AssumeRolePolicyDocument"]["Statement"],
                role["nested_policy"],
            )
        except Exception as e:
            print(f'Error updating policy document statements for {role["name"]}: {e}')
            sys.exit(1)

    return data


# Custom YAML dumper to ensure that the output is indented correctly
class IndentedDumper(yaml.Dumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False):
        return super().increase_indent(flow, False)


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Utility to update the default CDK bootstrapping YAML file with CMS-specific role properties.',
        epilog='Note that any errors during processing will result in the script exiting with a non-zero status code. '
               'This is intentional to prevent a bad bootstrapping attempt if the template is not updated correctly.',
    )
    parser.add_argument('role_file', type=str, help='JSON file containing the role information as a list of dictionaries')
    parser.add_argument('input_template', type=str, help='YAML file containing the default CDK bootstrapping template')
    parser.add_argument('output_template', type=str, help='YAML file to write the updated CDK bootstrapping template to')
    parser.add_argument('--boundary-policy-arn', type=str, default=BOUNDARY_POLICY_ARN,
                        help=f'ARN of the permissions boundary policy to attach to the roles. Default: "{BOUNDARY_POLICY_ARN}".')
    parser.add_argument('--role-to-assume-arn', type=str, default=ROLE_TO_ASSUME_ARN,
                        help=f'ARN of the role to be added to the AssumeRolePolicyDocument. Default: "{ROLE_TO_ASSUME_ARN}".')
    parser.add_argument('--role-path', type=str, default=ROLE_PATH,
                        help=f'Path to be added to the role properties. Default: "{ROLE_PATH}".')
    args = parser.parse_args()

    BOUNDARY_POLICY_ARN = args.boundary_policy_arn
    ROLE_TO_ASSUME_ARN = args.role_to_assume_arn
    ROLE_PATH = args.role_path

    # Read the file containing role information
    try:
        with open(args.role_file, 'r') as f:
            roles = json.load(f)
    except FileNotFoundError:
        print(f'Role file {args.role_file} not found')
        sys.exit(1)

    # Read the input CDK bootstrap template YAML file
    try:
        with open(args.input_template, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f'Input template file {args.input_template} not found')
        sys.exit(1)

    # Process each role in the role file
    for role in roles:
        if not all(["name" in role, "update_policy" in role, "nested_policy" in role]):
            print('Role information must contain "name", "update_policy", and "nested_policy" keys')
            sys.exit(1)
        name = role["name"]

        if name not in data["Resources"]:
            print(f'Role "{name}" not found in template')
            sys.exit(1)

        data["Resources"][name] = process_role(role, data["Resources"][name])

    # Write the updated template to the output file
    with open(args.output_template, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, Dumper=IndentedDumper)

    print(f'Updated template written to {args.output_template}')
    sys.exit(0)
