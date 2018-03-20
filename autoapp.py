# -*- coding: utf-8 -*-
"""Create an application instance."""
from dotenv import load_dotenv
import os

# if dotenv file, load it now
dotenv_path = os.environ.get('HXARC_DOTENV_PATH', None)
if dotenv_path:
    load_dotenv(dotenv_path)


from flask.helpers import get_debug_flag

from hxarc.app import create_app
from hxarc.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = create_app(CONFIG)
