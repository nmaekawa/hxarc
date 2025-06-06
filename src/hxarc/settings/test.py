import importlib.util
import os

from dotenv import load_dotenv

from hxarc.settings.base import *

dotenv_path = os.environ.get("HXARC_DOTENV_PATH", None)
if dotenv_path:
    load_dotenv(dotenv_path)

DEBUG = True

HXLTI_ENFORCE_SSL = False

LOGGING["loggers"]["django.db"] = {
    "level": "DEBUG",
    "handlers": ["console"],
    "propagate": True,
}

# Django Extensions
# http://django-extensions.readthedocs.org/en/latest/
spec = importlib.util.find_spec("django_extensions")
if spec:
    import django_extensions  # noqa

    INSTALLED_APPS += ["django_extensions"]

# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
spec = importlib.util.find_spec("debug_toobar")
if spec:
    import debug_toolbar  # noqa

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
