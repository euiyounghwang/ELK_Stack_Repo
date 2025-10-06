#!/bin/bash

set -eu

SCRIPTDIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo $SCRIPTDIR


docker run --rm -it -d \
  --name fn-nodejs-basic-api --publish 4000:3000 --expose 3000 \
  --network bridge \
#   -e ES_HOST=http://host.docker.internal:9203 \
  -v "$SCRIPTDIR:/app" \
  fn-nodejs-basic-api:es

