#!/bin/bash
set -xeu

echo "Apply migrations"



python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"

