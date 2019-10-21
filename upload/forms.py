from django import forms

class UploadFileForm(forms.Form):
    input_filename = forms.FileField()



