// src/config/environment-config.ts
import { Environment, EnvironmentConfig } from './types/config-types';

export const ENVIRONMENT_CONFIGS: Record<Environment, EnvironmentConfig> = {
  dev: {
    account: '009160033411',
    region: 'us-east-1',
  },
  val: {
    account: '222222222222',
    region: 'us-east-1',
  },
  prod: {
    account: '333333333333',
    region: 'us-east-1',
  },
};
