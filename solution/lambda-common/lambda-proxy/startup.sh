#!/bin/sh
python ${LAMBDA_TASK_ROOT}/lambda_common/lambda-proxy/lambda_proxy.py ${HOSTNAME} ${EXTERNAL_PORT} ${PROXY_PARAMS} &
exec /lambda-entrypoint.sh ${STARTUP_CMD}
