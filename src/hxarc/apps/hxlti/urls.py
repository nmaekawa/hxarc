from django.urls import re_path

import hxarc.apps.hxlti.views as views

urlpatterns = [
    re_path(r"^launch/", views.lti_landing_page, name="lti_landing"),
]
