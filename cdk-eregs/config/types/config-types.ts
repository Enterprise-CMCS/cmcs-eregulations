// config/types/config-types.ts
import * as cdk from 'aws-cdk-lib';

export type Environment = 'dev' | 'val' | 'prod' | 'experimental';

export interface BaseConfig {
  environment: Environment;
  stackPrefix: string;
  accountId: string;
  region: string;
  isExperimental: boolean;
  tags: Record<string, string>;
}

export interface VpcConfig {
  vpcId: string;
  privateSubnetIds: string[];
  publicSubnetIds: string[];
}

export interface IamConfig {
  path: string;
  permissionsBoundaryPolicy: string;
}

export interface CommonConfig {
  stage: string;
  logLevel: string;
  fismaTag: string;
  loggingAppName: string;
}

export interface ParserConfig {
  memorySize: number;
  timeout: number;
  queueRetentionDays: number;
  queueVisibilityTimeout: number;
}

export interface RedirectConfig {
  httpUser: string;
  httpPassword: string;
  apiStageName: string;
}



export interface MaintenanceConfig {
  allowedIps: string[];
  maintenanceWindow: string;
}
export interface StaticAssetsConfig {
  buckets: {
    assets: {
      name: string;
      versioned: boolean;
      retentionDays: number;
      noncurrentVersionRetentionDays: number;
    };
    logs: {
      name: string;
      retentionDays: number;
    };
  };
  cloudfront: {
    enabled: boolean;
    priceClass: 'PRICE_CLASS_100' | 'PRICE_CLASS_200' | 'PRICE_CLASS_ALL';
    ttl: {
      default: number;
      min: number;
      max: number;
    };
    enableCompression: boolean;
    enableLogging: boolean;
    logFilePrefix: string;
  };
  waf: {
    enabled: boolean;
    rateLimitThreshold: number;
    allowedCountries: string[];
  };
  deployment: {
    memoryLimit: number;
    prune: boolean;
  };
}
