# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import os
import logging
import logging.config
import yaml

from flask import flash


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


# from http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
def setup_logging(
        app,
        default_level=logging.INFO):
    """
    set up logging config.

    :param: app: application obj; relevant app.config['LOG_CONFIG']
            which is the full path to the yaml file with configs for logs
    :param: default_level: log level for basic config, default=INFO
    """
    if os.path.exists(app.config['LOG_CONFIG']):
        with open(app.config['LOG_CONFIG'], 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_exts(filename):
    """
    expects a filename that ends with something like `<filename>.tar.gz`

    returns the 2 rightmost extension as string `<ext>.<ext>`
    """
    if filename.count('.') > 1:
        (garbage, ext1, ext2) = filename.rsplit('.', 2)
        return '{}.{}'.format(ext1.lower(), ext2.lower())
    return None
