#!/usr/bin/env bash

set -euo pipefail

echo $HXARC_DOTENV_PATH
python manage.py migrate --noinput
python manage.py migrate hxlti --noinput
python manage.py collectstatic --noinput
python manage.py create_user --username 'user' --password 'password' --is_admin --force-update
exec python manage.py runserver 0.0.0.0:8000


