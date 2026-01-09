#!/bin/sh
uv run --directory ${LAMBDA_TASK_ROOT}/app python /proxy/lambda_proxy.py ${HOSTNAME} ${EXTERNAL_PORT} ${PROXY_PARAMS} &
exec /lambda-entrypoint.sh ${STARTUP_CMD}
