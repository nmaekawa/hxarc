
import logging
import re

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


def validate_filename(filename, valid_exts):
    """ validates upload filename, splits basename and ext.

    assumes valid_exts is a list of file extension,
        each file extension must include preceding `dot`
        e.g. ['.json', '.txt', '.csv']
    orders matter in this list. Say you have
        filename:  'file.tar.gz'
        exts: ['.gz', '.tar.gz']
    the result is ('file.tar', 'gz')
    """
    for ext in valid_exts:
        i = filename.find(ext)
        if i > 0:
            try:
                basename = re.sub(r'\W+', '-', filename[:i-1])
            except Exception as e:
                logger.error('invalid filename({}) for exts({}): {}'.format(
                    filename, valid_exts, e))
                return (None, None)
            else:
                return (basename, ext[1:])
    return (None, None)

