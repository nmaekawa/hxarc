
import logging
import os
import subprocess
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from hxlti.decorators import require_lti_launch
from .forms import UploadFileForm
from .util import get_exts
from .util import unpack_custom_parameters

logger = logging.getLogger(__name__)

@csrf_exempt
@xframe_options_exempt  # allows rendering in Canvas|edx frame
@require_lti_launch
def lti_upload(request):

    form = UploadFileForm()
    return render(
        request, 'upload/upload_form.html', {
            'form': form,
        })


def upload_file(request):
    '''
    global subproc_version
    if subproc_version is None:
        subproc_version = get_subproc_version(
            settings.HXARC_SCRIPT_PATH, 'hx_util')
        logger.info('{} - version {}'.format(__name__, subproc_version))
    '''

    if request.method != 'POST':
        #flash_errors(form)
        form = UploadFileForm()
        return render(
            request,
            'upload/upload_form.html',
            { 'form': form,
            #version=hxarc_version,
            #subproc_version=subproc_version
            }
        )

    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        tarball = request.FILES['course_tarball']

        logger.info('---------------- type({}) name({})'.format(
            type(tarball), tarball.name
        ))

        fs = FileSystemStorage()

        # save uploaded file in a subdir of HXARC_UPLOAD_DIR;
        # this subdir is a uuid, so pretty sure it's unique named
        ext = get_exts(tarball.name)

        logger.info('----------------- get_exts({})'.format(ext))

        upid = str(uuid.uuid4())
        updir = '{}/{}'.format(settings.HXARC_UPLOAD_DIR, upid)
        os.mkdir(updir)  # create a dir for each upload
        upfilename = os.path.join(
            updir, '{}.{}'.format(settings.HXARC_UPLOAD_FILENAME, ext))
        actual_filename = fs.save(upfilename, tarball)

        logger.debug('uploaded file({}) as ({})'.format(
            tarball.name, upfilename))


        command = '{} {}'.format( settings.HXARC_SCRIPT_PATH, upfilename)


        try:
            result = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            output_html = e.output.decode(
                'utf-8', 'ignore').strip().replace('\n', '<br/>')
            msg = 'exit code[{}] - {}'.format(
                e.returncode, e.output)
            logger.debug('COMMAND: ({}) -- {}'.format(
                command,
                e.output.decode('utf-8', 'ignore').strip(),
            ))
            return render(
                request,
                'upload/error.html',
                #version=hxarc_version,
                #subproc_version=subproc_version,
            )

        # success
        logger.debug('COMMAND: ({}) -- exit code[0] --- result({})'.format(
            command, result.decode('utf-8', 'ignore').strip()))

        #return render(
        #    request,
        #    'upload/result_link.html',
        #    upload_id=upid,
        #    version=hxarc_version,
        #    subproc_version=subproc_version,
        #)
        return render(request, 'upload.html', {'form': form})




