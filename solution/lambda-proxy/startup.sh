#!/bin/sh
python /proxy/lambda_proxy.py ${HOSTNAME} ${EXTERNAL_PORT} ${PROXY_PARAMS} &
exec /lambda-entrypoint.sh ${STARTUP_CMD}
