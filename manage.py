#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

from dotenv import load_dotenv


def main():
    """Run administrative tasks."""

    # if dotenv file, load it
    if "HXARC_DOTENV_PATH" in os.environ:
        dotenv_path = os.environ["HXARC_DOTENV_PATH"]
        load_dotenv(dotenv_path)

    # define default settings if not in environment
    if os.environ.get("DJANGO_SETTINGS_MODULE", None) is None:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hxarc.settings.local")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
