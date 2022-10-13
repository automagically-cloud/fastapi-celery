#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

celery -A worker.celery flower \
    --port=5555 \
    --loglevel=${CELERY_FLOWER_LOGLEVEL:INFO} \
    --natural_time \
    --debug=${CELERY_DEBUG:False} \
    --broker=$CELERY_BROKER_URL \
    --broker_api=$CELERY_BROKER_API_URL \
    --basic_auth=$CELERY_FLOWER_BASIC_AUTH
