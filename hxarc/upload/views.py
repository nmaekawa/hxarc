# -*- coding: utf-8 -*-
"""User views."""

import os
import uuid

from flask import Blueprint
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_login import login_required

from hxarc import app
from hxarc.upload.forms import UploadForm


blueprint = Blueprint('upload', __name__, url_prefix='/upload', static_folder='../static')


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    """upload form for course export."""

    form = UploadForm(request.form)
    if form.validate_on_submit():
        f = form.upfile.data

        upid = str(uuid.uuid4())
        updir = '{}/{}'.format(app.config['UPLOAD_FOLDER'], upid)
        os.mkdir(updir)
        filename = '{}.{}'.format(UPLOAD_FILENAME, ext)
        upfilename = os.path.join(updir, filename)
        f.save(upfilename)
        f.close()

        app.logger.debug('saved file in {}'.format(upfilename))

        #command = '{} {} {}'.format(app.config['SCRIPT_PATH'],
        #                            upfilename,
        #                            updir)
        #app.logger.debug('--------------- command: {}'.format(command))

        #result = subprocess.check_output(
        #    command,
        #    stderr=subprocess.STDOUT,
        #    shell=True
        #)
        #app.logger.debug('xxxxxxxxxxxxxxxxxxxxxxxx --- result({})'.format(result))

        return redirect(url_for('download_result', upload_id=upid))

    else:
        return render_template('upload/upload_form.html', form=form)



@blueprint.route('/<upload_id>')
def download_result(upload_id):
    app.logger.debug('in uploaded_file: id is {}'.format(upload_id))
    updir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
    return send_from_directory(updir, 'result.tsv')
