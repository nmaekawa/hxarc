"""
Django settings for hxarc project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import json
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
SETTINGS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SETTINGS_DIR)
PROJECT_NAME = "hxarc"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("HXARC_DJANGO_SECRET_KEY", "CHANGE_ME")

# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
allowed_hosts_other = os.environ.get("HXARC_ALLOWED_HOSTS", "")
if allowed_hosts_other:
    ALLOWED_HOSTS.extend(allowed_hosts_other.split())


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "hxlti",
    "hxarc.apps.upload",
    "corsheaders",
]

MIDDLEWARE = [
    "django_cookies_samesite.middleware.CookiesSameSite",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = PROJECT_NAME + ".urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = PROJECT_NAME + ".wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
HXARC_DB_PATH = os.environ.get(
    "HXARC_DB_PATH", os.path.join(BASE_DIR, PROJECT_NAME + "_sqlite3.db")
)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": HXARC_DB_PATH,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = []


# Logging config
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": (
                "%(asctime)s|%(levelname)s [%(filename)s:%(funcName)s]" " %(message)s"
            )
        },
        "syslog": {
            "format": (
                "%(levelname)s [%(filename)s:%(funcName)s:%(lineno)s]" " %(message)s"
            )
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "syslog",
            "stream": "ext://sys.stdout",
        },
        "errorfile_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": os.path.join(BASE_DIR, PROJECT_NAME + "_errors.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 7,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "upload": {"level": "DEBUG", "handlers": ["console"], "propagate": True},
        "hxarc": {"level": "DEBUG", "handlers": ["console"], "propagate": True},
        "hxlti": {"level": "DEBUG", "handlers": ["console"], "propagate": True},
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.environ.get(
            "HXARC_FILE_CACHE_DIR", os.path.join(BASE_DIR, "hxarc_filecache")
        ),
        "TIMETOUT": 86400,  # 1 day
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.environ.get("HXARC_STATIC_ROOT", os.path.join(BASE_DIR, "static/"))
MEDIA_URL = "/media/"
MEDIA_ROOT = os.environ.get("HXARC_MEDIA_ROOT", os.path.join(BASE_DIR, "media/"))

# hxlti app settings
# assuming ssl terminator in front of django (nginx reverse proxy)
use_ssl = os.environ.get("HXLTI_ENFORCE_SSL", "false")
HXLTI_ENFORCE_SSL = use_ssl.lower() == "true"
HXLTI_DUMMY_CONSUMER_KEY = os.environ.get(
    "HXLTI_DUMMY_CONSUMER_KEY", "dummy_734AFC14F318412FACA63AC5AF01414D"
)
HXLTI_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

#
# settings for django-cors-headers
#
CORS_ORIGIN_ALLOW_ALL = True  # accept requests from anyone

# replace when django 3.1, see https://github.com/jotes/django-cookies-samesite
# due to chrome 80.X, see https://www.chromium.org/updates/same-site
DCS_SESSION_COOKIE_SAMESITE = "None"
DCS_CSRF_COOKIE_SAMESITE = "None"

# django checks if it's trying to write files (uploads) outside
# BASE_DIR or MEDIA_ROOT...
HXARC_UPLOAD_DIR = MEDIA_ROOT
HXARC_UPLOAD_FILENAME = os.environ.get("HXARC_UPLOAD_FILENAME", "export")
HXARC_INPUT_FILENAME_JSON = os.environ.get(
        "HXARC_INPUT_FILENAME_JSON", "hxarc_input_data.json")

"""
hxarc expectations about subprocs:
1. to execute: <wrapper_path> <input_file>, where input_file valid
    extensions are in list <exts_in_upload>
2. subproc accepts argument `version_only` and prints out its version number
    without any other text, e.g. "2.4.4"
3. subproc prints out error messages that can be send to log to help debug
4. subproc generates an output file in the same dir as the given input file,
    and the output filename is <output_basename>.<output_ext>
"""
HXARC_SUBPROCS = {
    "sample": {
        # for extra inputs, create a new form to support needed form fields
        "form_classname": "hxarc.apps.upload.forms.UploadFileForm",
        "form_template_path": "upload/upload_form.html",
        "wrapper_path": os.path.join(BASE_DIR, "files/hxarc_wrapper.sh"),
        # subproc display_name in html
        "display_name": "fake",
        # text in form for label of filename to be uploaded
        "display_label": "course export tarball",
        # subproc output filename
        "output_basename": "result",  # internal output filename
        "output_ext": "tar.gz",  # internal output filename
        # upload file valid extensions; it's a list and each item must have the
        # '.' dot prefix; order is important as the first item that matches the
        # upload filename will be considered the proper extension
        "exts_in_upload": [".tar.gz", ".gz"],
    },
}
# this replaces default 'sample' subproc
hxarc_subprocs = json.loads(os.environ.get("HXARC_SUBPROCS", "{}"))
if hxarc_subprocs:
    HXARC_SUBPROCS = hxarc_subprocs

# this adds to hxarc_subprocs
extra_subprocs = json.loads(os.environ.get("HXARC_SUBPROCS_EXTRA", "{}"))
HXARC_SUBPROCS.update(extra_subprocs)