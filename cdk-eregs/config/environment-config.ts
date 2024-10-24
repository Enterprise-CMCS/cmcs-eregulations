

// config/environment-config.ts
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {
  BaseConfig,
  VpcConfig,
  IamConfig,
  CommonConfig,
  ParserConfig,
  RedirectConfig,
  StaticAssetsConfig,
  MaintenanceConfig,
  Environment
} from './types/config-types';

export interface EnvironmentStackProps extends cdk.StackProps {
  stage?: string;
}

export class EnvironmentConfigStack extends cdk.Stack {
  public readonly baseConfig: BaseConfig;
  public readonly vpcConfig: VpcConfig;
  public readonly iamConfig: IamConfig;
  public readonly commonConfig: CommonConfig;
  public readonly parserConfig: ParserConfig;
  public readonly redirectConfig: RedirectConfig;
  public readonly staticAssetsConfig: StaticAssetsConfig;
  public readonly maintenanceConfig: MaintenanceConfig;

  private ssmCache: Map<string, string> = new Map();

  constructor(scope: Construct, id: string, props?: EnvironmentStackProps) {
    super(scope, id, props);

    const branchName = process.env.GIT_BRANCH || 'dev';
    const environment = this.getEnvironmentFromBranch(branchName);
    const isExperimental = environment === 'experimental';

    this.baseConfig = this.initializeBaseConfig(environment, isExperimental);
    this.vpcConfig = this.loadVpcConfig();
    this.iamConfig = this.loadIamConfig();
    this.commonConfig = this.loadCommonConfig();
    this.parserConfig = this.loadParserConfig(isExperimental);
    this.redirectConfig = this.loadRedirectConfig(environment);
    this.staticAssetsConfig = this.loadStaticAssetsConfig();
    this.maintenanceConfig = this.loadMaintenanceConfig(environment);

    // Export configurations as CloudFormation outputs
    this.createOutputs();
  }

//   private getEnvironmentFromBranch(branch: string): Environment {
//     if (branch === 'main') return 'dev';
//     if (branch === 'val') return 'val';
//     if (branch === 'production') return 'prod';
//     return 'experimental';
//   }
  private getSsmParameter(path: string, defaultValue?: string): string {
    // Check cache first
    if (this.ssmCache.has(path)) {
      return this.ssmCache.get(path)!;
    }
  
    try {
      const value = ssm.StringParameter.valueForStringParameter(this, path);
      this.ssmCache.set(path, value);
      return value;
    } catch (error) {
      if (defaultValue === undefined) {
        throw new Error(`Required SSM parameter not found: ${path}`);
      }
      console.warn(`Parameter ${path} not found, using default value: ${defaultValue}`);
      return defaultValue;
    }
  }
  
  // Then the maintenance config can remain unchanged:
  private loadMaintenanceConfig(environment: string): MaintenanceConfig {
    return {
      allowedIps: this.getSsmParameter(
        `/eregulations/${environment}/maintenance/allowed_ips`,
        '[]'
      ).split(',').filter(ip => ip.trim()),
      
      maintenanceWindow: this.getSsmParameter(
        `/eregulations/${environment}/maintenance/window`,
        '0 0 * * 0'  // Default to midnight on Sundays
      ),
      
      notification: {
        enabled: !this.baseConfig.isExperimental,
        snsTopicArn: this.getSsmParameter(
          `/eregulations/${environment}/maintenance/notification_topic`,
          ''
        ),
        reminderHours: 24,
      },
      
      backup: {
        enabled: !this.baseConfig.isExperimental,
        retentionDays: this.baseConfig.isExperimental ? 1 : 30,
        schedule: this.baseConfig.isExperimental ? 'rate(1 day)' : 'rate(6 hours)',
      },
      
      monitoring: {
        metrics: {
          enabled: !this.baseConfig.isExperimental,
          namespace: 'Maintenance',
          dimensions: {
            Environment: environment,
            Service: 'eRegulations',
          },
        },
        alarms: {
          enabled: !this.baseConfig.isExperimental,
          errorThreshold: this.baseConfig.isExperimental ? 5 : 2,
          evaluationPeriods: this.baseConfig.isExperimental ? 1 : 3,
        },
      },
    };
  }

  private initializeBaseConfig(environment: Environment, isExperimental: boolean): BaseConfig {
    const accountIds = {
      dev: '009160033411',
      val: '222222222222',
      prod: '333333333333',
      experimental: '009160033411'
    };

    return {
      environment,
      stackPrefix: isExperimental ? 'exp' : environment,
      accountId: accountIds[environment],
      region: 'us-east-1',
      isExperimental,
      tags: {
        Environment: environment,
        Project: 'eregulations',
        ManagedBy: 'CDK'
      }
    };
  }

  private loadVpcConfig(): VpcConfig {
    return {
      vpcId: this.getSsmParameter('/account_vars/vpc/id'),
      privateSubnetIds: [
        this.getSsmParameter('/account_vars/vpc/subnets/private/a/id'),
        this.getSsmParameter('/account_vars/vpc/subnets/private/b/id')
      ],
      publicSubnetIds: [
        this.getSsmParameter('/account_vars/vpc/subnets/public/a/id'),
        this.getSsmParameter('/account_vars/vpc/subnets/public/b/id')
      ]
    };
  }
  private loadIamConfig(): IamConfig {
    return {
        path: this.getSsmParameter('/account_vars/iam/path'),
        permissionsBoundaryPolicy: this.getSsmParameter('/account_vars/iam/permissions_boundary_policy')

    }
  }
  private loadCommonConfig(): CommonConfig {
    const { environment } = this.baseConfig;
    
    // Load required parameters
    const commonConfig: CommonConfig = {
      stage: this.getSsmParameter(`/eregulations/${environment}/stage`, environment),
      logLevel: this.getSsmParameter(`/eregulations/${environment}/log_level`, 'INFO'),
      fismaTag: this.getSsmParameter('cms-cloud-cdm-support-fisma-tag', 'LOW'),
      loggingAppName: this.getSsmParameter('cms-cloud-logging-application-name', 'eregulations'),
      httpEndpoint: this.getSsmParameter(`/eregulations/${environment}/http_endpoint`, ''),
      // Add default retention settings
      retentionDays: this.baseConfig.isExperimental ? 1 : 14,
      // Add monitoring settings
      monitoring: {
        enabled: !this.baseConfig.isExperimental,
        alarmTopicArn: this.getSsmParameter(`/eregulations/${environment}/alarm_topic_arn`, ''),
      }
    };
  
    return commonConfig;
  }
  
  private loadParserConfig(isExperimental: boolean): ParserConfig {
    const baseMemory = isExperimental ? 512 : 1024;
    const baseTimeout = isExperimental ? 150 : 300;
  
    return {
      memorySize: baseMemory,
      timeout: baseTimeout,
      queueRetentionDays: isExperimental ? 1 : 14,
      queueVisibilityTimeout: baseTimeout,
      batchSize: isExperimental ? 1 : 10,
      concurrentExecutions: isExperimental ? 2 : 5,
      retryAttempts: isExperimental ? 1 : 3,
      dockerOptions: {
        maxConcurrency: isExperimental ? 2 : 4,
        memoryReservation: baseMemory,
      },
      cacheSettings: {
        enabled: !isExperimental,
        ttlMinutes: isExperimental ? 5 : 60,
      },
      monitoring: {
        enabled: !isExperimental,
        errorThreshold: isExperimental ? 5 : 3,
        warningThreshold: isExperimental ? 3 : 1,
      }
    };
  }
  
  private loadRedirectConfig(environment: string): RedirectConfig {
    return {
      httpUser: this.getSsmParameter(`/eregulations/${environment}/http_user`),
      httpPassword: this.getSsmParameter(`/eregulations/${environment}/http_password`),
      apiStageName: this.baseConfig.isExperimental ? 'exp' : environment,
      rateLimiting: {
        enabled: !this.baseConfig.isExperimental,
        rateLimit: this.baseConfig.isExperimental ? 100 : 1000,
        burstLimit: this.baseConfig.isExperimental ? 50 : 500,
      },
      caching: {
        enabled: !this.baseConfig.isExperimental,
        ttlSeconds: this.baseConfig.isExperimental ? 60 : 3600,
      },
      cors: {
        enabled: true,
        allowedOrigins: ['*'],
        allowedMethods: ['GET', 'POST', 'OPTIONS'],
        allowedHeaders: ['Content-Type', 'Authorization'],
        maxAge: 3600,
      },
      logging: {
        level: this.baseConfig.isExperimental ? 'DEBUG' : 'INFO',
        retention: this.baseConfig.isExperimental ? 3 : 30,
      }
    };
  }
  
  private loadStaticAssetsConfig(): StaticAssetsConfig {
    const { environment, stackPrefix, isExperimental } = this.baseConfig;
    
    return {
      buckets: {
        assets: {
          name: `eregs-${stackPrefix}-site-assets`,
          versioned: !isExperimental,
          retentionDays: isExperimental ? 7 : 365,
          noncurrentVersionRetentionDays: isExperimental ? 1 : 90,
        },
        logs: {
          name: `eregs-${stackPrefix}-cloudfront-logs`,
          retentionDays: isExperimental ? 7 : 90,
        },
      },
      cloudfront: {
        enabled: true,
        priceClass: isExperimental ? 'PRICE_CLASS_100' : 'PRICE_CLASS_ALL',
        ttl: {
          default: isExperimental ? 60 : 3600,
          min: 0,
          max: isExperimental ? 300 : 86400,
        },
        enableCompression: true,
        enableLogging: true,
        logFilePrefix: 'cf-logs/',
      },
      waf: {
        enabled: true,
        rateLimitThreshold: isExperimental ? 100 : 2000,
        allowedCountries: ['GU', 'PR', 'US', 'UM', 'VI', 'MP', 'AS'],
      },
      deployment: {
        memoryLimit: isExperimental ? 512 : 1024,
        prune: true,
      },
    };
  }
 
  // ... (implement other load methods)

  private createOutputs(): void {
    // Create outputs for cross-stack references
    Object.entries(this.baseConfig).forEach(([key, value]) => {
      new cdk.CfnOutput(this, `BaseConfig${key}`, {
        value: value.toString(),
        exportName: `${this.baseConfig.stackPrefix}-${key}`
      });
    });
    // ... create outputs for other configs
  }
}