import { IAspect } from "aws-cdk-lib";
import { IConstruct } from "constructs";
import * as iam from "aws-cdk-lib/aws-iam";
import { CfnResource } from "aws-cdk-lib";

export class IamPathAspect implements IAspect {
    private readonly iamPath: string;

    constructor(iamPath: string) {
        this.iamPath = iamPath;
    }

    public visit(node: IConstruct): void {
    // Check if the node is an instance of the higher-level iam.Role construct
        if (node instanceof iam.Role) {
            const roleResource = node.node.defaultChild as iam.CfnRole;
            roleResource.addPropertyOverride("Path", this.iamPath);
        }
        // Check if the node is an instance of a low-level CloudFormation resource (CfnRole)
        else if (node instanceof iam.CfnRole) {
            node.addPropertyOverride("Path", this.iamPath);
        }

        // Check if the node is an instance of the higher-level iam.User construct
        if (node instanceof iam.User) {
            const userResource = node.node.defaultChild as iam.CfnUser;
            userResource.addPropertyOverride("Path", this.iamPath);
        }
        // Check if the node is an instance of a low-level CloudFormation resource (CfnUser)
        else if (node instanceof iam.CfnUser) {
            node.addPropertyOverride("Path", this.iamPath);
        }

        // Check if the node is an instance of the higher-level iam.Group construct
        if (node instanceof iam.Group) {
            const groupResource = node.node.defaultChild as iam.CfnGroup;
            groupResource.addPropertyOverride("Path", this.iamPath);
        }
        // Check if the node is an instance of a low-level CloudFormation resource (CfnGroup)
        else if (node instanceof iam.CfnGroup) {
            node.addPropertyOverride("Path", this.iamPath);
        }

        // General checks for low-level CloudFormation resources
        if (CfnResource.isCfnResource(node)) {
            if ((node as CfnResource).cfnResourceType === "AWS::IAM::Role") {
                (node as iam.CfnRole).addPropertyOverride("Path", this.iamPath);
            } else if ((node as CfnResource).cfnResourceType === "AWS::IAM::User") {
                (node as iam.CfnUser).addPropertyOverride("Path", this.iamPath);
            } else if ((node as CfnResource).cfnResourceType === "AWS::IAM::Group") {
                (node as iam.CfnGroup).addPropertyOverride("Path", this.iamPath);
            }
        }
    }
}