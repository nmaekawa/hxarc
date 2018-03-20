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

from hxarc.upload.forms import UploadForm
from hxarc.utils import flash_errors
from hxarc.utils import get_exts


blueprint = Blueprint('upload', __name__, url_prefix='/upload', static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    """upload form for course export."""
    logger = logging.getLogger(__name__)
    logger.info('--- this is a log message from app: {}'.format(__name__))

    form = UploadForm()

    if form.validate_on_submit():
        f = form.course_export.data
        ext = get_exts(f.filename)

        upid = str(uuid.uuid4())
        updir = '{}/{}'.format(current_app.config['UPLOAD_DIR'], upid)
        os.mkdir(updir)  # create a dir for each upload
        upfilename = os.path.join(
            updir,
            '{}.{}'.format(current_app.config['UPLOAD_FILENAME'], ext))
        f.save(upfilename)
        f.close()

        command = '{} {} {}'.format(
            current_app.config['SCRIPT_PATH'], upfilename, updir)
        logger.debug('--------------- command: {}'.format(command))

        try:
            result = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            logger.debug('ERROR ERROR ERROR ERROR --- result([{}] - {})'.format(
                e.returncode, e.output))
            raise e

        # success
        logger.debug('xxxxxxxxxxxxxxxxxxxxxxxx --- result({})'.format(result))

        return redirect(url_for('upload.download_result', upload_id=upid))

    else:
        flash_errors(form)
        return render_template('upload/upload_form.html', form=form)



@blueprint.route('/<string:upload_id>/', methods=['GET'])
@login_required
def download_result(upload_id):
    logger = logging.getLogger(__name__)
    logger.debug('####################### in uploaded_file: id is {}'.format(upload_id))
    logger.debug('####################### upload_id type is {}'.format(type(upload_id)))
    updir = os.path.join(current_app.config['UPLOAD_DIR'], upload_id)
    return send_from_directory(updir, 'result.tsv')
