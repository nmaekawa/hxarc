# -*- coding: utf-8 -*-
"""User views."""

import logging
import os
import subprocess
import uuid

from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import redirect
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_login import login_required
from flask_login import current_user

from hxarc import __version__ as hxarc_version
from hxarc.utils import flash_errors
from hxarc.utils import get_exts


blueprint = Blueprint('maintenance', __name__, url_prefix='/maintenance', static_folder='../static')


@blueprint.route('/', methods=['GET'])
@login_required
def info():
    """print git sha of subproc and webapp."""
    logger = logging.getLogger(__name__)
    logger.info('--- this is a log message from app: {}[{}]'.format(__name__,
                                                                    current_user.is_admin))

    if not current_user.is_admin:
        return render_template('403.html', version=hxarc_version)

    # authorized to check this
    command = 'cd $(dirname {}) && git rev-parse --short HEAD'.format(
        current_app.config['SCRIPT_PATH'])
    logger.debug('--------------- command: {}'.format(command))

    try:
        result = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError as e:
        msg = 'ERROR ERROR ERROR ERROR --- result([{}] - {})'.format(
            e.returncode, e.output)
        logger.debug(msg)
        return render_template('upload/error.html', message=msg,
                                   version=hxarc_version)

    # success
    logger.debug('xxxxxxxxxxxxxxxxxxxxxxxx --- result({})'.format(
        result.decode('utf-8', 'backslashreplace').strip()))

    return render_template(
        'maintenance/version.html',
        script_name=os.path.basename(current_app.config['SCRIPT_PATH']),
        script_version=result.decode('utf-8', 'backslashreplace').strip())


