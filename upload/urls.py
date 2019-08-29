
from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('launch/', views.lti_upload, name='launch'),
    path('result/<slug:upload_id>/', views.download_result, name='result'),
]

# BEWARE that configs are not being tested for valid url path and names
for subproc in settings.HXARC_SUBPROCS:
    urlpatterns.append(path('{}/'.format(subproc),
                            views.upload_file,
                            {'subproc_id': subproc},
                            name=subproc,
                           ))


