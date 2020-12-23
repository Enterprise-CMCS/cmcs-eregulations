#!/bin/bash

set -e

if [[ $# -eq 0 ]]; then
  echo "Please enter in an API key as an argument and try again."
  exit 1
fi

pushd regulations-core
if git apply --check ../patches/regcore-jsonschema.patch; then
  git apply ../patches/regcore-jsonschema.patch
fi
popd

pushd regulations-parser
if git apply --check ../patches/regparser-Dockerfile.patch; then
  git apply ../patches/regparser-Dockerfile.patch
fi
popd

pushd config/static-assets
make build
popd

docker-compose up -d
sleep 2
docker-compose exec regulations-core python manage.py migrate
docker-compose exec regulations-core python manage.py rebuild_pgsql_index
docker-compose restart regulations-core

docker build --tag eregs_parser_kaitlin regulations-parser

./load_data.sh $1 pipeline 42 400 http://localhost:8080
