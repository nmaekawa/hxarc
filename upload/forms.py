from django import forms

class UploadFileForm(forms.Form):
    course_tarball = forms.FileField()



