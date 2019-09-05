
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
    """ expects a filename that ends with something like `<filename>.tar.gz`

    returns the 2 rightmost extension as string `<ext>.<ext>`
    """
    if filename.count('.') > 1:
        (garbage, ext1, ext2) = filename.rsplit('.', 2)
        return '{}.{}'.format(ext1.lower(), ext2.lower())
    return None




