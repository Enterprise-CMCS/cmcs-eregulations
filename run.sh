#!/bin/bash

if [[ $# -eq 0 ]]; then
  echo "Please enter in an API key as an argument and try again."
  exit 1
fi

cd regulations-core
git apply ../patches/regcore-jsonschema.patch
cd ..
cd regulations-parser
git apply ../patches/regparser-Dockerfile.patch
cd ..

docker-compose up -d
sleep 2
docker-compose exec regulations-core python manage.py migrate
docker-compose restart regulations-core
docker-compose exec regulations-site /usr/bin/build_static.sh

docker build --no-cache --tag eregs_parser_kaitlin regulations-parser

./load_data.sh $1 pipeline 42 400 http://localhost:8080
