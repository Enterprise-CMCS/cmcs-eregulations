# Parser Lambdas (Local Development)

This directory contains local and deploy-time code for the parser Lambda services:

- `ecfr-worker`
- `fr-worker`
- `ecfr-launcher`
- `fr-launcher`
- `common` (shared parsing/auth/config helpers)

## Local Docker setup

Parser local services use Lambda base images and `lambda-proxy`, matching the text-extractor local runtime approach.

From `solution/`:

```bash
make parsers.local.build
make parsers.local.up
```

If parser Dockerfiles or shared `common` code changes, rebuild parser services before invoking launchers.

Proxy endpoints exposed on localhost:

- `ecfr-worker`: `http://localhost:8003`
- `fr-worker`: `http://localhost:8004`
- `ecfr-launcher`: `http://localhost:8005`
- `fr-launcher`: `http://localhost:8006`

Stop local parser services:

```bash
make parsers.local.down
```

Stream logs:

```bash
make parsers.local.logs
```

Invoke schedulers via Make:

```bash
make parsers.local.invoke.ecfr-launcher
make parsers.local.invoke.fr-launcher
```

Run parser unit tests:

```bash
make parsers.test
```

## Invoke examples

### eCFR worker

```bash
curl -s -X POST http://localhost:8003 \
  -H 'Content-Type: application/json' \
  -d '{
    "Records": [
      {
        "body": "{\"config\": {\"title_number\": 42, \"part_number\": 400, \"credentials\": {\"auth_type\": \"basic\", \"username\": \"dev-user\", \"password\": \"dev-pass\"}}}"
      }
    ]
  }'
```

### FR worker

```bash
curl -s -X POST http://localhost:8004 \
  -H 'Content-Type: application/json' \
  -d '{
    "Records": [
      {
        "body": "{\"config\": {\"document_number\": \"2026-12345\", \"credentials\": {\"auth_type\": \"basic\", \"username\": \"dev-user\", \"password\": \"dev-pass\"}}}"
      }
    ]
  }'
```

### eCFR launcher

```bash
curl -s -X POST http://localhost:8005 \
  -H 'Content-Type: application/json' \
  -d '{}'
```

Example response in local mode:

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"enqueued\":1,\"local_mode\":true,\"succeeded\":1,\"failed\":0,\"failures\":[],\"work_units\":[...]}"
}
```

### FR launcher

```bash
curl -s -X POST http://localhost:8006 \
  -H 'Content-Type: application/json' \
  -d '{}'
```

Example response in local mode:

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"enqueued\":1,\"local_mode\":true,\"succeeded\":1,\"failed\":0,\"failures\":[],\"work_units\":[...]}"
}
```

## Notes

- Launchers run with `PARSER_LOCAL_MODE=true` in Docker Compose and call workers over HTTP (`PARSER_WORKER_URL`) via lambda-proxy.
- In deployed environments, `PARSER_LOCAL_MODE` is unset and launchers use `PARSER_QUEUE_URL` to enqueue work.
- Workers accept either a single SQS-style record event (`Records[0].body`) or a lambda-proxy HTTP event body.
- Credentials are resolved in workers (not passed by launchers): first from message payload if valid, then `EREGS_AUTH_SECRET_NAME` (AWS Secrets Manager), then `EREGS_BEARER_TOKEN`, then `EREGS_USERNAME`/`EREGS_PASSWORD`.
