# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired


class UploadForm(FlaskForm):
    """Upload form."""
    upfile = FileField(
        label='course export "tar.gz"',
        validators=[
            FileRequired(),
            FileAllowed(['gz'], 'tar.gzip course exports'),
        ],
    )
