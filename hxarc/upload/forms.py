# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired


# TODO: make this configurable
UPLOAD_FIELD_LABEL = 'course export tarball'
UPLOAD_FIELD_ALLOWED_EXTENSIONS = ['tar.gz', 'tar']

class UploadForm(FlaskForm):
    """Upload form."""
    course_export = FileField(
        label=UPLOAD_FIELD_LABEL,
        validators=[
            FileRequired(),
            FileAllowed(
                UPLOAD_FIELD_ALLOWED_EXTENSIONS,
                'course export must have extension `tar.gz`'),
        ])




