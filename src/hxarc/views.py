
from django.http import HttpResponse

from hxarc import __name__ as hxarc_name
from hxarc import __version__ as hxarc_version
from hxarc import vpal_version_comment


# version info
def info(request):
    return HttpResponse(
        "{} v{} - {}".format(
            hxarc_name,
            hxarc_version,
            vpal_version_comment,
        )
    )

