from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from hxarc.apps.hxlti.decorators import require_lti_launch


@csrf_exempt
@xframe_options_exempt  # allows rendering in Canvas|edX iframe
@require_lti_launch
def lti_landing_page(request):
    return render(request, "hxlti/index.html")
