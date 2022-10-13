#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

celery -A worker.celery worker \
    -E \
    --loglevel $CELERY_WORKER_LOGLEVEL \
    --hostname $CELERY_WORKER_NAME@%h \
    --concurrency $CELERY_WORKER_CONCURRENCY \
    --queues $CELERY_WORKER_QUEUES
