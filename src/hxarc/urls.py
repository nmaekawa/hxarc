"""hxarc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# import hxarc.apps.hkey.views as hkey_views
from django_vkey import views as vkey_views

import hxarc.apps.upload.views as upload_views
import hxarc.views as hxarc_views

urlpatterns = [
    path(settings.HXARC_ADMIN_URL_PATH, admin.site.urls),
    path("upload/", include("hxarc.apps.upload.urls")),
    path("info/", hxarc_views.info, name="info"),
    path(
        "index/",
        vkey_views.hkey_index,
        {"service_view": upload_views.upload_landing},
        name="index",
    ),
    path(
        os.path.join(settings.SAML_URL_PATH, "metadata/"),
        vkey_views.metadata,
        name="saml_metadata",
    ),
    path(
        settings.SAML_URL_PATH,
        vkey_views.saml,
        {"service_view": upload_views.upload_landing},
        name="saml",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
