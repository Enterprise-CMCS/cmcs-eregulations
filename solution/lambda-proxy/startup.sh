#!/bin/sh
python /proxy/lambda_proxy.py ${HOSTNAME} ${INTERNAL_PORT} ${EXTERNAL_PORT} &
exec /lambda-entrypoint.sh ${STARTUP_CMD}
