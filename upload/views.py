
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

logger = logging.getLogger(__name__)

@csrf_exempt
@xframe_options_exempt  # allows rendering in Canvas|edx frame
@require_lti_launch
def lti_upload(request):

    logger.debug('--------- hxarc_version=({})'.format(hxarc_version))
    logger.debug('--------- HXARC_SUBPROC_APPS=({})'.format(settings.HXARC_SUBPROC_APPS))
    logger.debug('--------- session=({})'.format(request.session))
    logger.debug('--------- session keys({})'.format(request.session.keys()))
    logger.debug('--------- session user_id=({})'.format(request.session['_auth_user_id']))


    # login user
    user_id = request.POST['user_id']
    user, created = User.objects.get_or_create(username=user_id,
                                               email='{}@hx.edu'.format(user_id))
    if created:
        logger.debug('--------- user CREATED({})'.format(user))
        user.set_unusable_password()
        user.save()
    else:
        logger.debug('--------- user FETCHED({})'.format(user))

    user.backend = 'django.contrib.auth.backend.ModelBackend'
    login(request, user)
    request.session['user_logged'] = user.id
    request.session.modified = True


    logger.debug('*********** ({}) logged in?({})'.format(
        request.user,
        request.user.is_authenticated))

    form = UploadFileForm()
    fake_url = reverse('fake')
    return render(
        request,
        'upload/landing.html',
        {
            'hxarc_version': hxarc_version,
            'form_action': fake_url,
            'hxarc_apps': settings.HXARC_SUBPROC_APPS,
        }
    )

def upload_file(request, subproc_name='fake'):
    '''
    global subproc_version
    if subproc_version is None:
        subproc_version = get_subproc_version(
            settings.HXARC_SCRIPT_PATH, 'hx_util')
        logger.info('{} - version {}'.format(__name__, subproc_version))
    '''
    logger.debug('--------- session=({})'.format(request.session))
    logger.debug('--------- session keys({})'.format(request.session.keys()))
    logger.debug('--------- session user_id=({})'.format(request.session['_auth_user_id']))
    logger.debug('--------- user_logged=({})'.format(request.session['user_logged']))


    logger.debug('*********** ({}) logged in?({})'.format(
        request.session['_auth_user_id'],
        request.user.id))

    if request.method != 'POST':
        #flash_errors(form)
        form = UploadFileForm()
        return render(
            request,
            'upload/upload_form.html',
            {
                'form': form,
                'hxarc_version': hxarc_version,
                'form_action': reverse(subproc_name),
                'hxarc_apps': settings.HXARC_SUBPROC_APPS,
                'app_name': subproc_name,
                'app_version': 'XX.YY.ZZ',
            #subproc_version=subproc_version
            }
        )

    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        tarball = request.FILES['course_tarball']
        fs = FileSystemStorage()

        # save uploaded file in a subdir of HXARC_UPLOAD_DIR;
        # this subdir is a uuid, so pretty sure it's unique named
        ext = get_exts(tarball.name)

        upid = str(uuid.uuid4())
        updir = '{}/{}'.format(settings.HXARC_UPLOAD_DIR, upid)
        os.mkdir(updir)  # create a dir for each upload
        upfilename = os.path.join(
            updir, '{}.{}'.format(settings.HXARC_UPLOAD_FILENAME, ext))
        actual_filename = fs.save(upfilename, tarball)

        logger.info('uploaded file({}) as ({})'.format(
            tarball.name, upfilename))


        command = '{} {}'.format(
            settings.HXARC_SUBPROC_APPS[subproc_name]['wrapper_path'],
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
            logger.warning('COMMAND: ({}) -- {}'.format(
                command,
                e.output.decode('utf-8', 'ignore').strip(),
            ))
            return render(
                request,
                'upload/error.html',
                {
                    'hxarc_version': hxarc_version,
                'hxarc_apps': settings.HXARC_SUBPROC_APPS,
                #subproc_version=subproc_version,
                }
            )

        # success
        logger.info('COMMAND: ({}) -- exit code[0] --- result({})'.format(
            command, result.decode('utf-8', 'ignore').strip()))
    else:
        form = UploadFileForm()

    return render(
        request,
        'upload/result_link.html',
        {
            'upload_id': upid,
            'hxarc_version': hxarc_version,
            'hxarc_apps': settings.HXARC_SUBPROC_APPS,
            'app_name': subproc_name,
            'app_version': 'XX.YY.ZZ',
        #subproc_version=subproc_version
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


