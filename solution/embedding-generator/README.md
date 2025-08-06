# Contents

1. [About](#about)
2. [Running locally](#running-locally)
3. [Request structure](#request-structure)
    1. [Configuring authentication](#configuring-authentication)
        1. [Basic auth](#basic-auth)
        2. [AWS Secrets Manager](#aws-secrets-manager)
        3. [Token auth](#token-auth)
4. [Response structure](#response-structure)

# About

This Lambda function is used to generate embeddings for (hybrid) semantic search.

# Running locally

This project uses Lambda docker containers to further the goal of making our deployed and development environments match. However, there are limitations of these containers:

- They do not natively emulate API Gateway.
- They do not accept more than one request at a time.

These limitations are being worked on, but in the meantime there is an additional dependency found in the [lambda-proxy](../lambda-common/lambda-proxy) directory. This program is copied into the Docker container on build and is transparent to the user. It takes standard HTTP requests/responses and translates them into the type of JSON-based requests/responses that Lambda functions expect. In effect, this proxy partially emulates API Gateway. See [here](https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html) for more information on Lambda request/response payload structure.

The generator will be automatically started when `docker-compose up -d --build` is run because eRegs depends on it.

No further action is required, but if you want the code to hot-reload during development, you may install `watchfiles` with `pip3 install watchfiles` and then run `make watch-embedding-generator`.

# Request structure

The following data structure is required:

```jsonc
{
    "id": 1234,                                 // A unique ID for the text chunk.
    "upload_url": "https://api-url-here/",      // The URL to upload the embeddings to.
    "text": "text to generate embeddings for",  // The text to generate embeddings for.
    "model_id": "amazon.titan-embed-text-v2:0", // Optional - the model to use, defaults to Titan V2.
    "dimensions": 512,                          // Optional - how many dimensions to use, defaults to 512.
    "normalize": true,                          // Optional - normalize the embeddings, defaults to true.
    // Only necessary to include if the PATCH endpoint uses authentication.
    "auth": {
        // See below for configuring authentication.
    },
    // Only necessary to include if running locally or current role does not permit the use of SQS or Bedrock
    "aws": {
        "aws_access_key_id": "xxxxxx",       // The access key for AWS, see below for details.
        "aws_secret_access_key": "xxxxxx",   // The AWS secret key, see below for details.
        "aws_region": "us-east-1"            // AWS region to use, see below for details.
    }
}
```

Note that under a typical setup, `aws_access_key_id`, `aws_secret_access_key`, and `aws_region` are not needed when running in AWS. This is true as long as your Lambda function has the appropriate permissions for Bedrock and SQS (if you're using it).

If you wish to directly invoke this function, you may do so like this:

```python
import boto3
import json

request = {
    # ...the structure from above goes here...
}

data = json.dumps(request).encode()  # JSONify the request and convert it to bytes

client = boto3.client("lambda")      # Include access keys/region here if needed
response = client.invoke(
    FunctionName="lambda-arn-here",
    InvocationType="Event",          # Include this if you want to run the lambda async, as recommended
    Payload=data,                    # You may include raw JSON here
)
```

## Configuring authentication

The embedding generator supports several authentication schemes.

### Basic auth

Direct basic auth which includes the credentials in the request:

```jsonc
"auth": {
    "type": "basic",
    "username": "xxxxxx",
    "password": "xxxxxx"
}
```

To use basic auth but retrieve the credentials from environment variables, configure like this:

```jsonc
"auth": {
    "type": "basic-env",
    "username": "USERNAME_ENV_VAR",
    "password": "PASSWORD_ENV_VAR"
}
```

### AWS Secrets Manager

For basic auth with credentials retrieved as JSON from AWS Secrets Manager, configure like this:

```jsonc
"auth": {
    "type": "basic-secretsmanager",
    "secret_name": "name of the secret in AWS",
    "username_key": "key for username field",
    "password_key": "key for password field"
}
```

You can also retrieve the secret name from an environment variable, like so:

```jsonc
"auth": {
    "type": "basic-secretsmanager-env",
    "secret_name": "env variable name containing the secret name",
    "username_key": "key for username field",
    "password_key": "key for password field"
}
```

### Token auth

To use token-based authentication, configure like this:

```jsonc
"auth": {
    "type": "token",
    "token": "xxxxxx"
}
```

# Response structure

When the function completes, it will attempt to send a JSON PATCH request to the URL specified in `upload_url`. The request will be sent whether the generator succeeds or fails. The contents will look like this:

```jsonc
{
    "id": 1234,                     // The unique ID of the resource
    "embeddings": [1, 2, 3, ...]    // The generated embeddings
}
```
