// lib/constructs/network-construct.ts

import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

enum SubnetType {
  PRIVATE = 'Private',
  PUBLIC = 'Public'
}

export interface NetworkConstructProps {
  stage: string;
  vpcId?: string;
  vpcAccountId?: string;
  vpcRegion?: string;
  privateSubnetIds?: string[];
  publicSubnetIds?: string[];
  subnetTags?: { [key: string]: string };
  availabilityZones?: string[];
}

export class NetworkConstruct extends Construct {
  public readonly vpc: ec2.IVpc;
  public readonly privateSubnets: ec2.ISubnet[];
  public readonly publicSubnets: ec2.ISubnet[];

  constructor(scope: Construct, id: string, props: NetworkConstructProps) {
    super(scope, id);

    this.validateProps(props);

    this.vpc = this.importVpc(props);
    console.log(`VPC imported successfully. VPC ID: ${this.vpc.vpcId}`);

    this.privateSubnets = this.importOrLookupSubnets(SubnetType.PRIVATE, props);
    this.publicSubnets = this.importOrLookupSubnets(SubnetType.PUBLIC, props);

    if (props.subnetTags) {
      this.tagSubnets([...this.privateSubnets, ...this.publicSubnets], props.subnetTags);
    }

    this.createOutputs(props.stage);
  }

  private validateProps(props: NetworkConstructProps): void {
    if (!props.stage) {
      throw new Error('Stage is required');
    }
  }

  private importVpc(props: NetworkConstructProps): ec2.IVpc {
    try {
      if (props.vpcId) {
        return ec2.Vpc.fromLookup(this, 'ImportedVPC', {
          vpcId: props.vpcId,
          ownerAccount: props.vpcAccountId,
          region: props.vpcRegion,
        });
      } else {
        return ec2.Vpc.fromLookup(this, 'DefaultVPC', { isDefault: true });
      }
    } catch (error) {
      const context = props.vpcId 
        ? `VPC ID: ${props.vpcId}, Account: ${props.vpcAccountId || 'current'}, Region: ${props.vpcRegion || 'current'}`
        : 'Default VPC';
      throw new Error(`Failed to import VPC (${context}): ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private importOrLookupSubnets(type: SubnetType, props: NetworkConstructProps): ec2.ISubnet[] {
    const subnetIds = type === SubnetType.PRIVATE ? props.privateSubnetIds : props.publicSubnetIds;
    if (subnetIds && subnetIds.length > 0) {
      return this.importSubnets(type, subnetIds, props.stage);
    } else {
      return this.lookupSubnets(
        type === SubnetType.PRIVATE ? ec2.SubnetType.PRIVATE_WITH_NAT : ec2.SubnetType.PUBLIC,
        props.availabilityZones
      );
    }
  }

  private importSubnets(type: SubnetType, subnetIds: string[], stage: string): ec2.ISubnet[] {
    if (!this.vpc.vpcId) {
      throw new Error('VPC ID is not available. Ensure the VPC is imported correctly before importing subnets.');
    }

    return subnetIds.map((subnetId, index) => {
      const subnet = ec2.Subnet.fromSubnetId(this, `${type}Subnet${index}-${stage}`, subnetId);
      if (subnet.vpcId !== this.vpc.vpcId) {
        throw new Error(`Subnet ${subnetId} does not belong to the specified VPC ${this.vpc.vpcId}. 
          Subnet VPC ID: ${subnet.vpcId}, Expected VPC ID: ${this.vpc.vpcId}`);
      }
      console.log(`Imported ${type} subnet: ${subnetId} in VPC: ${this.vpc.vpcId}`);
      return subnet;
    });
  }

  private lookupSubnets(subnetType: ec2.SubnetType, availabilityZones?: string[]): ec2.ISubnet[] {
    const selection = this.vpc.selectSubnets({ 
      subnetType,
      availabilityZones: availabilityZones && availabilityZones.length > 0 ? availabilityZones : undefined
    });
    console.log(`Found ${selection.subnets.length} ${subnetType} subnets`);
    return selection.subnets;
  }

  private tagSubnets(subnets: ec2.ISubnet[], tags: { [key: string]: string }): void {
    subnets.forEach(subnet => {
      Object.entries(tags).forEach(([key, value]) => {
        cdk.Tags.of(subnet).add(key, value);
      });
    });
    console.log(`Tagged ${subnets.length} subnets with ${Object.keys(tags).length} tags`);
  }

  private createOutputs(stage: string): void {
    const outputProps = [
      { id: 'VpcId', value: this.vpc.vpcId, description: 'VPC ID' },
      { id: 'PrivateSubnetIds', value: this.privateSubnets.map(subnet => subnet.subnetId).join(','), description: 'Private Subnet IDs' },
      { id: 'PublicSubnetIds', value: this.publicSubnets.map(subnet => subnet.subnetId).join(','), description: 'Public Subnet IDs' },
    ];

    outputProps.forEach(({ id, value, description }) => {
      new cdk.CfnOutput(this, id, {
        value,
        description: `${description} for ${stage} environment`,
        exportName: `${this.node.id}-${stage}-${id}`,
      });
    });
  }

  public getSubnetsByAz(): { [az: string]: { private?: ec2.ISubnet, public?: ec2.ISubnet } } {
    const subnetMap: { [az: string]: { private?: ec2.ISubnet, public?: ec2.ISubnet } } = {};

    this.privateSubnets.forEach(subnet => {
      if (!subnetMap[subnet.availabilityZone]) {
        subnetMap[subnet.availabilityZone] = {};
      }
      subnetMap[subnet.availabilityZone].private = subnet;
    });

    this.publicSubnets.forEach(subnet => {
      if (!subnetMap[subnet.availabilityZone]) {
        subnetMap[subnet.availabilityZone] = {};
      }
      subnetMap[subnet.availabilityZone].public = subnet;
    });

    return subnetMap;
  }
}