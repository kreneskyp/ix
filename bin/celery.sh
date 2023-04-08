#! /bin/bash
set -o errexit

celery -A ix worker --loglevel=info