#! /bin/bash
set -o errexit

CELERY_CONCURRENCY=${CELERY_CONCURRENCY:=1}
DJANGO_SETTINGS_MODULE=ix.server.celery_settings

# celery runs in SOLO pool to avoid concurrency issues with asyncio
# this means that concurrency is limited to 1, even if set to a higher
# value. A longer term solution is likely needed to support concurrency
# within a single celery worker.
celery -A ix worker --loglevel=info --pool=solo --concurrency=${CELERY_CONCURRENCY}