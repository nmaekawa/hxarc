"""
WSGI config for hxarc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

from dotenv import load_dotenv
import os

from django.core.wsgi import get_wsgi_application


# if dotenv file, load it
dotenv_path = os.environ.get(
    'HXARC_DOTENV_PATH', None)
if dotenv_path:
    load_dotenv(dotenv_path)

# set default if not in environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hxarc.settings.prod")

application = get_wsgi_application()
