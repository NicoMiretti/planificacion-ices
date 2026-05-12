#!/usr/bin/env bash
# build.sh — script de build para Render
set -o errexit

pip install -r requirements/production.txt

python manage.py collectstatic --no-input
python manage.py migrate
