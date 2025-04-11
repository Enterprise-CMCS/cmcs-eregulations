import { IAspect, CfnResource, Stack } from 'aws-cdk-lib';
import { IConstruct } from 'constructs';

export class IamPermissionsBoundaryAspect implements IAspect {
    private readonly permissionsBoundaryArn: string;

    constructor(permissionsBoundaryArn: string) {
        this.permissionsBoundaryArn = permissionsBoundaryArn;
    }

    public visit(node: IConstruct): void {
        if (node instanceof CfnResource && node.cfnResourceType === 'AWS::IAM::Role') {
            node.addPropertyOverride('PermissionsBoundary', this.permissionsBoundaryArn);
        }
    }
}