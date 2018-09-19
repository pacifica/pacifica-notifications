#!/bin/bash -xe
if python -V 2>&1 | grep 'Python 2' ; then
  pip install -r requirements2-dev.txt
else
  pip install -r requirements-dev.txt
fi
psql -c 'create database pacifica_metadata;' -U postgres
export POSTGRES_ENV_POSTGRES_USER=postgres
export POSTGRES_ENV_POSTGRES_PASSWORD=
pushd travis/metadata
MetadataServer.py &
popd
MAX_TRIES=60
HTTP_CODE=$(curl -sL -w "%{http_code}\\n" localhost:8121/keys -o /dev/null || true)
while [[ $HTTP_CODE != 200 && $MAX_TRIES > 0 ]] ; do
  sleep 1
  HTTP_CODE=$(curl -sL -w "%{http_code}\\n" localhost:8121/keys -o /dev/null || true)
  MAX_TRIES=$(( MAX_TRIES - 1 ))
done
TOP_DIR=$PWD
MD_TEMP=$(mktemp -d)
git clone https://github.com/pacifica/pacifica-metadata.git ${MD_TEMP}
pushd ${MD_TEMP}
python test_files/loadit.py
popd
pushd travis/policy
PolicyServer.py &
echo $! > PolicyServer.pid
popd
pushd test_files
python cherrypy_catch.py &
echo $! > cherrypy-catch.pid
popd
