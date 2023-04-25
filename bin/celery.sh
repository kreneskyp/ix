#! /bin/bash
set -o errexit

CELERY_CONCURRENCY=${CELERY_CONCURRENCY:=1}
DJANGO_SETTINGS_MODULE=ix.server.celery_settings

celery -A ix worker --loglevel=info --concurrency=${CELERY_CONCURRENCY}