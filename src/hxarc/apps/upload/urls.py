from django.conf import settings
from django.urls import path

from hxarc.apps.upload import views

urlpatterns = [
    path("launch/", views.lti_upload, name="launch"),
    path("index/", views.hkey_upload, name="hkey"),
    path("landing/", views.upload_landing, name="landing"),
    path("saml/", views.saml, name="saml"),
    path("info/", views.info, name="info"),
    path("result/<slug:upload_id>/", views.download_result, name="result"),
]

# BEWARE that configs are not being tested for valid url path and names
for subproc in settings.HXARC_SUBPROCS:
    urlpatterns.append(
        path(
            "{}/".format(subproc),
            views.upload_file,
            {"subproc_id": subproc},
            name=subproc,
        )
    )
