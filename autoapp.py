# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

from hxarc.app import create_app
from hxarc.settings import DevConfig, ProdConfig


# TODO: add dotenv

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)
