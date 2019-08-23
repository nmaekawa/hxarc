
from django.urls import path

from . import views

urlpatterns = [
    path('launch/', views.lti_upload, name='launch'),
    path('upload/', views.upload_file, name='upload'),
    path('result/<slug:upload_id>/', views.download_result, name='result'),
]

