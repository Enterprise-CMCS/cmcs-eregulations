import { SecretsManagerClient, GetSecretValueCommand, CreateSecretCommand } from "@aws-sdk/client-secrets-manager";

const client = new SecretsManagerClient({ region: 'us-east-1' });

const secretPaths = [
  '/eregulations/db/credentials',
  '/eregulations/http/credentials',
  '/eregulations/http/django_credentials',
  '/eregulations/http/reader_credentials',
  '/eregulations/oidc/credentials'
];

async function copySecret(sourcePath: string, targetPath: string) {
  try {
    const getCommand = new GetSecretValueCommand({ SecretId: sourcePath });
    const response = await client.send(getCommand);

    const createCommand = new CreateSecretCommand({
      Name: targetPath,
      SecretString: response.SecretString,
      Description: `Copied from ${sourcePath}`
    });

    await client.send(createCommand);
    console.log(`✅ Copied ${sourcePath} to ${targetPath}`);
  } catch (error) {
    console.error(`❌ Failed to copy ${sourcePath}:`, error);
  }
}

async function main() {
  for (const path of secretPaths) {
    // Copy existing secret to dev environment
    await copySecret(
      path,
      path.replace('/eregulations/', '/eregulations/dev/')
    );

    // Create new prod secret with same structure but different values
    await copySecret(
      path,
      path.replace('/eregulations/', '/eregulations/prod/')
    );
  }
}

main().catch(console.error);