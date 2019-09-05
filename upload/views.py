
import logging
import os
import subprocess
import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt


from hxarc import __version__ as hxarc_version
from hxlti.decorators import require_lti_launch
from .forms import UploadFileForm
from .util import get_exts
from .util import unpack_custom_parameters

subproc_version = None
logger = logging.getLogger(__name__)

def landing(request):
    return render(
        request,
        'upload/landing.html',
        {
            'hxarc_version': hxarc_version,
            'hxarc_subprocs': settings.HXARC_SUBPROCS,
        }
    )


@csrf_exempt
@xframe_options_exempt  # allows rendering in Canvas|edx frame
@require_lti_launch
def lti_upload(request):

    # fetch or create lti user
    # counting it's in edx, and properly configured to send username
    username = request.POST['lis_person_sourcedid']
    user, created = User.objects.get_or_create(username=username,
                                               email='{}@hx.edu'.format(username))

    # login user
    login(request, user)

    # pick first configured subproc
    subproc_id = list(settings.HXARC_SUBPROCS0[0]
    subproc_conf = settings.HXARC_SUBPROCS[subproc_id]

    global subproc_version
    if subproc_version is None:
        subproc_version = {}
    if subproc_id not in subproc_version:
        subproc_version[subproc_id] = get_subproc_version(
            subproc_conf['wrapper_path'])
        logger.info('[{}] {} - version {}'.format(
            request.user.username,
            __name__, subproc_version
        ))

    form = UploadFileForm()
    return render(
        request,
        'upload/upload_form.html',
        {
            'hxarc_version': hxarc_version,
            'hxarc_subprocs': settings.HXARC_SUBPROCS,
            'form': form,
            'form_action': reverse(subproc_id),
            'subproc_name': subproc_conf['display_name'],
            'subproc_version': subproc_version[subproc_id],
        }
    )


@login_required
def upload_file(request, subproc_id='sample'):
    subproc_conf = settings.HXARC_SUBPROCS[subproc_id]

    global subproc_version
    if subproc_version is None:
        subproc_version = {}
    if subproc_id not in subproc_version:
        subproc_version[subproc_id] = get_subproc_version(
            subproc_conf['wrapper_path'])
        logger.info('[{}] {} - version {}'.format(
            request.user.username,
            __name__, subproc_version
        ))


    if request.method != 'POST':
        #flash_errors(form)
        form = UploadFileForm()
        return render(
            request,
            'upload/upload_form.html',
            {
                'hxarc_version': hxarc_version,
                'hxarc_subprocs': settings.HXARC_SUBPROCS,
                'form': form,
                'form_action': reverse(subproc_id),
                'subproc_name': subproc_conf['display_name'],
                'subproc_version': subproc_version[subproc_id],
            }
        )

    upid = str(uuid.uuid4())
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        tarball = request.FILES['course_tarball']
        fs = FileSystemStorage()

        # save uploaded file in a subdir of HXARC_UPLOAD_DIR;
        # this subdir is a uuid, so pretty sure it's unique named
        ext = get_exts(tarball.name)

        updir = '{}/{}'.format(settings.HXARC_UPLOAD_DIR, upid)
        os.mkdir(updir)  # create a dir for each upload
        upfilename = os.path.join(
            updir, '{}.{}'.format(settings.HXARC_UPLOAD_FILENAME, ext))
        actual_filename = fs.save(upfilename, tarball)

        logger.info('[{}] uploaded file({}) as ({})'.format(
            request.user.username,
            tarball.name, upfilename))


        command = '{} {}'.format(
            subproc_conf['wrapper_path'],
            upfilename
        )


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
            logger.warning('[{}] COMMAND: ({}) -- {}'.format(
                request.user.username,
                command,
                e.output.decode('utf-8', 'ignore').strip(),
            ))
            return render(
                request,
                'upload/error.html',
                {
                    'hxarc_version': hxarc_version,
                    'hxarc_subprocs': settings.HXARC_SUBPROCS,
                    'subproc_name': subproc_conf['display_name'],
                    'subproc_version': subproc_version[subproc_id],
                }
            )

        # success
        logger.info('[{}] COMMAND: ({}) -- exit code[0] --- result({})'.format(
            request.user.username,
            command, result.decode('utf-8', 'ignore').strip()))
    else:
        form = UploadFileForm()

    return render(
        request,
        'upload/result_link.html',
        {
            'upload_id': upid,
            'hxarc_version': hxarc_version,
            'hxarc_subprocs': settings.HXARC_SUBPROCS,
            'subproc_name': subproc_conf['display_name'],
            'subproc_version': subproc_version[subproc_id],
        }
    )


@login_required
def download_result(request, upload_id):
    upfile = os.path.join(settings.HXARC_UPLOAD_DIR, upload_id, 'result.tar.gz')
    if os.path.exists(upfile):
        with open(upfile, 'rb') as fh:
            response = HttpResponse(
                fh.read(),
                content_type='application/gzip',
            )
            response['Content-Disposition'] = 'inline; filename=' + \
                    'hxarc_{}.tar.gz'.format(upload_id)
        return response
    else:
        return Http404;


def get_subproc_version(script_path):
    """execute wrapper script to get subproc version."""

    logger = logging.getLogger(__name__)
    command = '{} version_only'.format(script_path)

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
        return 'version not available'

    # success
    version = result.decode('utf-8', 'ignore').strip()
    logger.debug('COMMAND: ({}) -- exit code[0] --- result({})'.format(
            command, version))

    return version

