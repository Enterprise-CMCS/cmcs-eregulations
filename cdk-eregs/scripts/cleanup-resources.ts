import {
  RDSClient,
  DeleteDBInstanceCommand,
  DescribeDBInstancesCommand,
  DeleteDBClusterCommand,
  DescribeDBClustersCommand,
  DeleteDBParameterGroupCommand,
  DeleteDBClusterParameterGroupCommand,
  DescribeDBParameterGroupsCommand,
  DescribeDBClusterParameterGroupsCommand,
  ModifyDBClusterCommand,
  DBInstance
} from "@aws-sdk/client-rds";
import {
  CloudWatchLogsClient,
  DeleteLogGroupCommand,
  DescribeLogGroupsCommand
} from "@aws-sdk/client-cloudwatch-logs";
import {
  S3Client,
  DeleteBucketCommand,
  ListObjectsV2Command,
  DeleteObjectCommand,
  HeadBucketCommand
} from "@aws-sdk/client-s3";

const rdsClient = new RDSClient({ region: 'us-east-1' });
const logsClient = new CloudWatchLogsClient({ region: 'us-east-1' });
const s3Client = new S3Client({ region: 'us-east-1' });

async function waitForDatabaseDeletion(dbInstance: DBInstance) {
  while (true) {
    try {
      const describeCommand = new DescribeDBInstancesCommand({
        DBInstanceIdentifier: dbInstance.DBInstanceIdentifier
      });
      await rdsClient.send(describeCommand);
      console.info(`Waiting for database ${dbInstance.DBInstanceIdentifier} to be deleted...`);
      await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
    } catch (error: any) {
      if (error?.$metadata?.httpStatusCode === 404) {
        console.info(`Database ${dbInstance.DBInstanceIdentifier} deleted`);
        break;
      }
      throw error;
    }
  }
}

async function deleteDatabases(prefix: string) {
  try {
    const describeCommand = new DescribeDBInstancesCommand({});
    const response = await rdsClient.send(describeCommand);

    for (const db of response.DBInstances || []) {
      if (db.DBInstanceIdentifier?.includes(prefix)) {
        console.info(`Found database: ${db.DBInstanceIdentifier}`);
        try {
          const deleteCommand = new DeleteDBInstanceCommand({
            DBInstanceIdentifier: db.DBInstanceIdentifier,
            SkipFinalSnapshot: true,
            DeleteAutomatedBackups: true
          });

          await rdsClient.send(deleteCommand);
          console.info(`✅ Started deletion of database ${db.DBInstanceIdentifier}`);
          await waitForDatabaseDeletion(db);
        } catch (error: any) {
          if (error?.Error?.Code === 'InvalidDBInstanceState' &&
              error?.Error?.Message?.includes('already being deleted')) {
            console.info(`Database ${db.DBInstanceIdentifier} is already being deleted`);
            await waitForDatabaseDeletion(db);
          } else {
            throw error;
          }
        }
      }
    }
  } catch (error) {
    console.error(`❌ Failed to delete databases with prefix ${prefix}:`, error);
  }
}

async function emptyAndDeleteBucket(bucketName: string) {
  try {
    // Check if bucket exists
    try {
      await s3Client.send(new HeadBucketCommand({ Bucket: bucketName }));
    } catch (error: any) {
      if (error?.$metadata?.httpStatusCode === 404) {
        console.info(`Bucket ${bucketName} does not exist, skipping`);
        return;
      }
      throw error;
    }

    // Empty the bucket first
    let continuationToken: string | undefined;
    do {
      const listCommand = new ListObjectsV2Command({
        Bucket: bucketName,
        ContinuationToken: continuationToken
      });

      const response = await s3Client.send(listCommand);

      for (const object of response.Contents || []) {
        if (!object.Key) continue;
        await s3Client.send(new DeleteObjectCommand({
          Bucket: bucketName,
          Key: object.Key
        }));
      }

      continuationToken = response.NextContinuationToken;
    } while (continuationToken);

    // Delete the empty bucket
    await s3Client.send(new DeleteBucketCommand({ Bucket: bucketName }));
    console.info(`✅ Deleted bucket ${bucketName}`);
  } catch (error) {
    console.error(`❌ Failed to delete bucket ${bucketName}:`, error);
  }
}

async function deleteDBClusters(prefix: string) {
  try {
    const describeCommand = new DescribeDBClustersCommand({});
    const response = await rdsClient.send(describeCommand);

    for (const cluster of response.DBClusters || []) {
      if (cluster.DBClusterIdentifier?.includes(prefix)) {
        console.info(`Found cluster: ${cluster.DBClusterIdentifier}`);

        // First, disable deletion protection
        const modifyCommand = new ModifyDBClusterCommand({
          DBClusterIdentifier: cluster.DBClusterIdentifier,
          DeletionProtection: false
        });

        await rdsClient.send(modifyCommand);
        console.info(`✅ Disabled deletion protection for cluster ${cluster.DBClusterIdentifier}`);

        // Then delete the cluster
        const deleteCommand = new DeleteDBClusterCommand({
          DBClusterIdentifier: cluster.DBClusterIdentifier,
          SkipFinalSnapshot: true
        });

        await rdsClient.send(deleteCommand);
        console.info(`✅ Started deletion of DB cluster ${cluster.DBClusterIdentifier}`);
      }
    }
  } catch (error) {
    console.error(`❌ Failed to delete DB clusters with prefix ${prefix}:`, error);
  }
}

async function deleteParameterGroups(prefix: string) {
  try {
    // Delete DB Parameter Groups
    const describeParamCommand = new DescribeDBParameterGroupsCommand({});
    const paramGroups = await rdsClient.send(describeParamCommand);

    for (const group of paramGroups.DBParameterGroups || []) {
      if (group.DBParameterGroupName?.includes(prefix)) {
        const deleteCommand = new DeleteDBParameterGroupCommand({
          DBParameterGroupName: group.DBParameterGroupName
        });
        await rdsClient.send(deleteCommand);
        console.info(`✅ Deleted DB parameter group ${group.DBParameterGroupName}`);
      }
    }

    // Delete DB Cluster Parameter Groups
    const describeClusterParamCommand = new DescribeDBClusterParameterGroupsCommand({});
    const clusterGroups = await rdsClient.send(describeClusterParamCommand);

    for (const group of clusterGroups.DBClusterParameterGroups || []) {
      if (group.DBClusterParameterGroupName?.includes(prefix)) {
        const deleteCommand = new DeleteDBClusterParameterGroupCommand({
          DBClusterParameterGroupName: group.DBClusterParameterGroupName
        });
        await rdsClient.send(deleteCommand);
        console.info(`✅ Deleted DB cluster parameter group ${group.DBClusterParameterGroupName}`);
      }
    }
  } catch (error) {
    console.error(`❌ Failed to delete parameter groups with prefix ${prefix}:`, error);
  }
}

async function deleteLogGroups(prefix: string) {
  try {
    const describeCommand = new DescribeLogGroupsCommand({
      logGroupNamePrefix: prefix
    });

    const response = await logsClient.send(describeCommand);

    for (const logGroup of response.logGroups || []) {
      if (!logGroup.logGroupName) continue;

      const deleteCommand = new DeleteLogGroupCommand({
        logGroupName: logGroup.logGroupName
      });

      await logsClient.send(deleteCommand);
      console.info(`✅ Deleted log group ${logGroup.logGroupName}`);
    }
  } catch (error) {
    console.error(`❌ Failed to delete log groups with prefix ${prefix}:`, error);
  }
}

async function main() {
  const environment = process.argv[2];
  if (!environment || !['dev', 'prod'].includes(environment)) {
    console.error('Please specify environment (dev/prod)');
    process.exit(1);
  }

  const prefix = `-${environment}-`;
  console.info(`Starting cleanup for resources containing: ${prefix}`);

  // Delete in correct order:
  // 1. S3 buckets first (no dependencies)
  await emptyAndDeleteBucket(`a1m-eregs-${environment}-file-repo-eregs`);

  // 2. Database instances first (they reference clusters and parameter groups)
  await deleteDatabases(prefix);

  // 3. Wait a bit for DB instance deletion to complete
  console.info('Waiting 30 seconds for database instances to finish deletion...');
  await new Promise(resolve => setTimeout(resolve, 30000));

  // 4. Then clusters (they reference parameter groups)
  await deleteDBClusters(prefix);

  // 5. Wait for cluster deletion
  console.info('Waiting 30 seconds for clusters to finish deletion...');
  await new Promise(resolve => setTimeout(resolve, 30000));

  // 6. Finally parameter groups (after all references are gone)
  await deleteParameterGroups(prefix);

  // 7. Log groups last (no dependencies)
  await deleteLogGroups(`/aws/lambda/a1m-eregs-${environment}`);
  await deleteLogGroups(`/aws/rds/a1m-eregs-${environment}`);
  await deleteLogGroups(`/aws/api-gateway/a1m-eregs-${environment}`);
  await deleteLogGroups(`/aws/api-gateway/a1m-eregs-${environment}-api`);
}

main().catch(console.error);