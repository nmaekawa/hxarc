#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv


def main():
    # if dotenv file, load it
    # check env var, then a default.env in project root
    dotenv_path = None
    if "HXARC_DOTENV_PATH" in os.environ:
        dotenv_path = os.environ["HXARC_DOTENV_PATH"]
    else:
        # check for default dotenv in project root
        managepy_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_env = os.path.join(managepy_dir, "default.env")
        if os.path.exists(default_env):
            dotenv_path = default_env
    if dotenv_path:
        load_dotenv(dotenv_path)

    # define settings if not in environment
    if os.environ.get("DJANGO_SETTINGS_MODULE", None) is None:
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "hxarc.settings.local"
        )

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
