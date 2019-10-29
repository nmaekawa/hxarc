import json
from django import forms


class JsonListField(forms.Field):
    def to_python(self, value):
        """coerces input into json."""
        try:
            json_field = json.loads(value)
        except Exception as e:
            raise forms.ValidationError(
                'Invalid json in exts field({}): {}'.format(value, e),
                code='invalid',
            )
        else:
            return json_field

    def validate(self, value):
        """input must be a list of strings."""
        super().validate(value)
        if not isinstance(value, list):
            raise forms.ValidationError(
                'Invalid exts field({}) : must be a list'.format(value),
                code='invalid',
            )


class UploadFileForm(forms.Form):
    input_filename = forms.FileField()
    exts = JsonListField()



