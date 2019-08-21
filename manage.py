#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from dotenv import load_dotenv
import os
import sys

if __name__ == "__main__":
    # default settings is "dev"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hxarc.settings.dev")

    # if dotenv file, load it
    dotenv_path = os.environ.get('HXARC_DOTENV_PATH', None)
    if dotenv_path:
        load_dotenv(dotenv_path)

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import my fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise

    execute_from_command_line(sys.argv)



