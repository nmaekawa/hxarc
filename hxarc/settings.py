# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('HXARC_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    BCRYPT_LOG_ROUNDS = 13

    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    ASSETS_DEBUG = True  # do not bundle/minify static assets
    WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'

    # log dir default is project root
    LOG_CONFIG = os.environ.get(
        'HXARC_LOG_CONFIG',
        os.path.join(PROJECT_ROOT, 'logging.yaml'))

    # pull upload configs from environ
    UPLOAD_DIR = os.environ.get('HXARC_UPLOAD_DIR', PROJECT_ROOT)
    UPLOAD_FILENAME = os.environ.get('HXARC_UPLOAD_FILENAME', 'export')
    ext_list = os.environ.get('HXARC_UPLOAD_EXTENSIONS', None)

    # pull process script from environ
    SCRIPT_PATH = os.environ.get(
        'HXARC_SCRIPT_PATH',
        os.path.join(PROJECT_ROOT, 'bin/hxarc_wrapper.sh'))


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'

    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar

    DB_PATH = os.environ.get(
        'HXARC_DB_PATH',
        os.path.join(Config.PROJECT_ROOT, 'database.db'))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'

    DEBUG = True
    DEBUG_TB_ENABLED = True

    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'

    TESTING = True
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    BCRYPT_LOG_ROUNDS = 4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
    WTF_CSRF_ENABLED = False  # Allows form testing
