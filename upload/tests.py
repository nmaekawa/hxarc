import pytest

from django.conf import settings

from upload.util import unpack_custom_parameters



def test_request_params_ok():
    pmap = settings.HXARC_CUSTOM_PARAMETERS_MAP
    rparams = {
        'custom_canvas_ids': 'canvas1; canvas2; canvas3',
        'custom_object_ids': 'manifest1; manifest2; manifest3',
        'custom_layout': '1x3',
        'custom_view_type': 'CrazyViewTypo',
    }

    lti_params = unpack_custom_parameters(rparams)

    print('result: ({})'.format(lti_params))

    assert(len(lti_params) == 4)
    assert(
        set(lti_params[pmap['custom_canvas_ids']['mapto']]) == \
        set(['canvas1', 'canvas2', 'canvas3'])
    )
    assert(
        set(lti_params[pmap['custom_object_ids']['mapto']]) == \
        set(['manifest1', 'manifest2', 'manifest3'])
    )
    assert(lti_params[pmap['custom_layout']['mapto']] == '1x3')
    assert(lti_params[pmap['custom_view_type']['mapto']] == 'CrazyViewTypo')


