import importlib.util

from hxarc.settings.dev import *  # noqa

DEBUG = True

HXLTI_ENFORCE_SSL = False

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
