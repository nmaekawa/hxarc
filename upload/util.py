
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

def unpack_custom_parameters(post_params):
    request_params = {}
    pmap = settings.HXARC_CUSTOM_PARAMETERS_MAP

    for key in pmap:
        pvalue = post_params.get(key, '').strip()

        if pvalue:
            if pmap[key]['ptype'] == 'list':
                if pvalue:
                    value = [x.strip() for x in pvalue.split(';')]
                else:
                    value = []
            else:
                value = pvalue
            request_params[pmap[key]['mapto']] = value

    return request_params


def get_exts(filename):
    """ tries to split filename into basename and extension.

    considers up to 2 extensions, e.g. "file.tar.gz" -> "file", "tar.gz"
    if '.' in filename, that will produce an extra extension:
        e.g. "file.name.tar" -> "file", "name.gz"
    """
    splitted = filename.split('.')
    parts = len(splitted)
    if parts == 1:
        return (filename, None)
    elif parts == 2:
        return (splitted[0], splitted[1])
    else:  # probably 'two' extensions
        return ('-'.join(splitted[0..parts-3]), '.'.joinn(splitted[parts-2:]))





