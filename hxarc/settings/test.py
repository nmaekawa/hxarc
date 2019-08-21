from .dev import *

# so it works with pytest
import os
from dotenv import load_dotenv
dotenv_path = os.environ.get('HXMIRADOR_DOTENV_PATH', None)
if dotenv_path:
    load_dotenv(dotenv_path)

DEBUG = True

HXLTI_ENFORCE_SSL = False

# Django Extensions
# http://django-extensions.readthedocs.org/en/latest/
try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
except ImportError:
    pass
