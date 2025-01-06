import { getParameterValue } from '../utils/parameter-store';
import { StageConfig } from '../config/stage-config';

export interface ApiConfig {
  environmentVariables: Record<string, string>;
  vpcId: string;
  certificateArn: string;
  httpUser: string;
  httpPassword: string;
}

export interface DatabaseConfig {
  username: string;
  password: string;
  port: string;
  host: string;
}

export async function loadConfiguration(stageConfig: StageConfig): Promise<ApiConfig> {
  const [
    vpcId,
    httpUser,
    httpPassword,
    certificateArn,
    dbPassword,
    dbHost,
    dbPort,
    gaId,
    readerUser,
    readerPassword,
    djangoSettings,
    baseUrl,
    customUrl,
    surveyUrl,
    signupUrl,
    demoVideoUrl,
    oidcClientId,
    oidcClientSecret,
    oidcAuthEndpoint,
    oidcTokenEndpoint,
    oidcJwksEndpoint,
    oidcUserEndpoint,
    oidcEndSession,
    basicSearchFilter,
    quotedSearchFilter,
    searchHeadlineTextMax,
    searchHeadlineMinWords,
    searchHeadlineMaxWords,
    searchHeadlineMaxFragments,
    euaFeatureFlag,
  ] = await Promise.all([
    getParameterValue('/account_vars/vpc/id'),
    getParameterValue('/eregulations/http/user'),
    getParameterValue('/eregulations/http/password'),
    getParameterValue('/eregulations/acm-cert-arn'),
    getParameterValue('/eregulations/db/password'),
    getParameterValue('/eregulations/db/host'),
    getParameterValue('/eregulations/db/port'),
    getParameterValue('/eregulations/http/google_analytics'),
    getParameterValue('/eregulations/http/reader_user'),
    getParameterValue('/eregulations/http/reader_password'),
    getParameterValue('/eregulations/django_settings_module'),
    getParameterValue('/eregulations/base_url'),
    getParameterValue('/eregulations/custom_url'),
    getParameterValue('/eregulations/survey_url'),
    getParameterValue('/eregulations/signup_url'),
    getParameterValue('/eregulations/demo_video_url'),
    getParameterValue('/eregulations/oidc/client_id'),
    getParameterValue('/eregulations/oidc/client_secret'),
    getParameterValue('/eregulations/oidc/authorization_endpoint'),
    getParameterValue('/eregulations/oidc/token_endpoint'),
    getParameterValue('/eregulations/oidc/jwks_endpoint'),
    getParameterValue('/eregulations/oidc/user_endpoint'),
    getParameterValue('/eregulations/oidc/end_eua_session'),
    getParameterValue('/eregulations/basic_search_filter'),
    getParameterValue('/eregulations/quoted_search_filter'),
    getParameterValue('/eregulations/search_headline_text_max'),
    getParameterValue('/eregulations/search_headline_min_words'),
    getParameterValue('/eregulations/search_headline_max_words'),
    getParameterValue('/eregulations/search_headline_max_fragments'),
    getParameterValue('/eregulations/eua/featureflag'),
  ]);

  return {
    vpcId,
    httpUser,
    httpPassword,
    certificateArn,
    environmentVariables: {
      DB_NAME: 'eregs',
      DB_USER: 'eregsuser',
      DB_PASSWORD: dbPassword,
      DB_HOST: dbHost,
      DB_PORT: dbPort,
      GA_ID: gaId,
      HTTP_AUTH_USER: httpUser,
      HTTP_AUTH_PASSWORD: httpPassword,
      DJANGO_USERNAME: readerUser,
      DJANGO_PASSWORD: readerPassword,
      DJANGO_ADMIN_USERNAME: httpUser,
      DJANGO_ADMIN_PASSWORD: httpPassword,
      DJANGO_SETTINGS_MODULE: djangoSettings,
      ALLOWED_HOST: '.amazonaws.com',
      STAGE_ENV: stageConfig.stage,
      BASE_URL: baseUrl,
      CUSTOM_URL: customUrl,
      SURVEY_URL: surveyUrl,
      SIGNUP_URL: signupUrl,
      DEMO_VIDEO_URL: demoVideoUrl,
      OIDC_RP_CLIENT_ID: oidcClientId,
      OIDC_RP_CLIENT_SECRET: oidcClientSecret,
      OIDC_OP_AUTHORIZATION_ENDPOINT: oidcAuthEndpoint,
      OIDC_OP_TOKEN_ENDPOINT: oidcTokenEndpoint,
      OIDC_OP_JWKS_ENDPOINT: oidcJwksEndpoint,
      OIDC_OP_USER_ENDPOINT: oidcUserEndpoint,
      OIDC_END_EUA_SESSION: oidcEndSession,
      BASIC_SEARCH_FILTER: basicSearchFilter,
      QUOTED_SEARCH_FILTER: quotedSearchFilter,
      SEARCH_HEADLINE_TEXT_MAX: searchHeadlineTextMax,
      SEARCH_HEADLINE_MIN_WORDS: searchHeadlineMinWords,
      SEARCH_HEADLINE_MAX_WORDS: searchHeadlineMaxWords,
      SEARCH_HEADLINE_MAX_FRAGMENTS: searchHeadlineMaxFragments,
      EUA_FEATUREFLAG: euaFeatureFlag,
      DEPLOY_NUMBER: process.env.RUN_ID || '',
    }
  };
}