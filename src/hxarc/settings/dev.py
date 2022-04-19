from hxarc.settings.base import *  # noqa

DEBUG = True

# add db logging to dev settings
LOGGING["loggers"]["django.db"] = {
    "level": "DEBUG",
    "handlers": ["console"],
    "propagate": True,
}
