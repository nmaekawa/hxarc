import json
import logging
import mimetypes
import os
import subprocess
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from hxarc import __name__ as hxarc_name
from hxarc import __version__ as hxarc_version
from hxarc import vpal_version_comment as vpal_version_comment

from hxarc.apps.hxlti.decorators import require_lti_launch

# from hxarc.apps.upload.forms import UploadFileForm
from hxarc.apps.upload.util import get_class_object, validate_filename

# saml2 for hkey
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.auth import OneLogin_Saml2_Auth


subproc_version = None
logger = logging.getLogger(__name__)


# version info
def info(request):
    return HttpResponse(
        "{} v{} - {}".format(
            hxarc_name,
            hxarc_version,
            vpal_version_comment,
        )
    )

@csrf_exempt
@xframe_options_exempt  # allows rendering in Canvas|edx frame
@require_lti_launch
def lti_upload(request):
    """lti user login

    expects to be requested as an lti 1.1 launch and logs in
    lti user into django app. If all goes well, presents upload
    landing page.
    """
    # fetch or create lti user
    # edx studio does not send a proper lti request; missing username
    username = request.POST.get("lis_person_sourcedid", None)
    if username is None:
        logger.error(
            (
                "missing lis_person_sourcedid in lti request; "
                "maybe in edge? referer: {}"
            ).format(request.META["HTTP_REFERER"])
        )
        return render_error(
            request,
            subproc_id=None,
            msgs=["malformed lti request"],
            status_code=401,
        )

    # login user
    hxarc_login_user(request, username)

    # return response from view upload_landing()
    return upload_landing(request)


@login_required
def upload_landing(request):
    # pick first configured subproc
    subproc_id = list(settings.HXARC_SUBPROCS)[0]
    subproc_conf = settings.HXARC_SUBPROCS[subproc_id]
    populate_subproc_version(subproc_id, subproc_conf)
    logger.info(
        "[{}] {} - version {}".format(
            request.user.username, __name__, subproc_version
        )
    )
    form = get_class_object(subproc_conf["form_classname"])()

    # render form for the first configured subproc
    return render(
        request,
        subproc_conf["form_template_path"],
        {
            "hxarc_version": hxarc_version,
            "hxarc_subprocs": settings.HXARC_SUBPROCS,
            "form": form,
            "form_action": reverse(subproc_id),
            "subproc_name": subproc_conf["display_name"],
            "subproc_version": subproc_version[subproc_id],
            "input_filename_label": subproc_conf.get(
                "display_label", "course export tarbal (.tar.gz)"
            ),
            "exts_in_upload": json.dumps(
                subproc_conf.get("exts_in_upload", [".tar.gz"])
            ),
        },
    )


@login_required
def upload_file(request, subproc_id="sample"):
    if subproc_id not in settings.HXARC_SUBPROCS:
        raise Http404("unknown subprocess({})".format(subproc_id))
    else:
        subproc_conf = settings.HXARC_SUBPROCS[subproc_id]

    populate_subproc_version(subproc_id, subproc_conf)
    logger.info(
        "[{}] {} - version {}".format(
            request.user.username, __name__, subproc_version
        )
    )

    if request.method != "POST":
        form = get_class_object(subproc_conf["form_classname"])()
        # newrun: set defaults into form
        return render(
            request,
            subproc_conf["form_template_path"],
            {
                "hxarc_version": hxarc_version,
                "hxarc_subprocs": settings.HXARC_SUBPROCS,
                "form": form,
                "form_action": reverse(subproc_id),
                "subproc_name": subproc_conf["display_name"],
                "subproc_version": subproc_version[subproc_id],
                "input_filename_label": subproc_conf.get(
                    "display_label", "course export tarball (.tar.gz)"
                ),
                "exts_in_upload": json.dumps(
                    subproc_conf.get("exts_in_upload", [".tar.gz"])
                ),
            },
        )

    upid = str(uuid.uuid4())
    form = get_class_object(subproc_conf["form_classname"])(request.POST, request.FILES)
    if form.is_valid():
        tarball = request.FILES["input_filename"]
        fs = FileSystemStorage()

        input_basename, input_ext = validate_filename(
            tarball.name, form.cleaned_data["exts"]
        )
        if input_basename is None or input_ext is None:
            msg = "invalid filename ({}): valid extensions {}".format(
                tarball.name, form.cleaned_data["exts"]
            )
            logger.error(msg)
            # invalid file extension
            return render_error(
                request,
                subproc_id,
                [msg],
                status_code=400,
            )

        # save uploaded file in a subdir of MEDIA_ROOT;
        # this subdir is a uuid, so pretty sure it's uniquely named
        updir = os.path.join(settings.MEDIA_ROOT, upid)
        os.mkdir(updir)  # create a dir for each upload
        upfullpath = os.path.join(
            updir, "{}.{}".format(settings.HXARC_UPLOAD_FILENAME, input_ext)
        )

        # FileSystemStorage does not like abs paths, so set relative path to MEDIA_ROOT
        uprelativepath = os.path.join(
            upid, "{}.{}".format(settings.HXARC_UPLOAD_FILENAME, input_ext)
        )
        fs.save(uprelativepath, tarball)

        # remove after saving bc cannot jsonify tarfile later
        # so, here, assuming input always have an uploaded file!
        del form.cleaned_data["input_filename"]

        # newrun: pack form inputs to feed to wrapper
        is_json_input = len(form.cleaned_data) > 1  # assuming exts always present
        if is_json_input:
            # serialize inputs
            input_data = form.todict()
            input_data["tarfile"] = (
                upfullpath  # TODO: this is specific to make_new_run!
            )
            input_path = os.path.join(
                updir,
                settings.HXARC_INPUT_FILENAME_JSON,
            )
            with open(input_path, "w") as ifd:
                ifd.write(json.dumps(input_data))

        cache.set(
            upid,
            {  # to be used in download
                "subproc_id": subproc_id,
                "original_filename": input_basename,
                "output_basename": subproc_conf.get("output_basename", "result"),
                "output_ext": subproc_conf.get("output_ext", "tar.gz"),
            },
        )

        logger.info(
            "[{}] uploaded file({}) as ({})".format(
                request.user.username, tarball.name, upfullpath
            )
        )

        command = "{} {}".format(subproc_conf["wrapper_path"], upfullpath)
        try:
            result = subprocess.check_output(
                command, stderr=subprocess.STDOUT, shell=True
            )
        except subprocess.CalledProcessError as e:
            # debug purposes
            # output_html = e.output.decode(
            #    'utf-8', 'ignore').strip().replace('\n', '<br/>')
            msg = "exit code[{}] - {}".format(e.returncode, e.output)
            logger.warning(
                "[{}] COMMAND: ({})|exit({}) -- {}".format(
                    request.user.username,
                    command,
                    e.returncode,
                    e.output.decode("utf-8", "ignore").strip(),
                )
            )
            return render_error(request, subproc_id)

        # success
        logger.info(
            "[{}] COMMAND: ({}) -- exit code[0] --- result({})".format(
                request.user.username, command, result.decode("utf-8", "ignore").strip()
            )
        )
    else:
        # form not valid! probably malformed exts config
        logger.error("form invalid: {}".format(form.errors))
        return render_error(request, subproc_id)

    return render(
        request,
        "upload/result_link.html",
        {
            "upload_id": upid,
            "hxarc_version": hxarc_version,
            "hxarc_subprocs": settings.HXARC_SUBPROCS,
            "subproc_name": subproc_conf["display_name"],
            "subproc_version": subproc_version[subproc_id],
        },
    )


@login_required
def download_result(request, upload_id):
    cache_info = cache.get(upload_id)
    if cache_info is None:
        msg = "invalid upload_id({})".format(upload_id)
        return render_error(request, subproc_id=None, msgs=[msg], status_code=404)

    upfile = os.path.join(
        settings.MEDIA_ROOT,  # saved in FileSytemStorage
        upload_id,
        "{}.{}".format(
            cache_info["output_basename"],
            cache_info["output_ext"],
        ),
    )

    if os.path.exists(upfile):
        mimetype, _ = mimetypes.guess_type(upfile)
        with open(upfile, "rb") as fh:
            response = HttpResponse(
                fh.read(),
                content_type=mimetype,
            )
            content_header = "attachment; filename=hxarc_{}.{}".format(
                cache_info["original_filename"],
                cache_info["output_ext"],
            )
            response["Content-Disposition"] = content_header
        return response
    else:
        msg = "expired upload_id({})".format(upload_id)
        logger.error(msg)
        return render_error(
            request, subproc_id=cache_info["subproc_id"], msgs=[msg], status_code=404
        )


def get_subproc_version(script_path):
    """execute wrapper script to get subproc version."""

    command = "{} version_only".format(script_path)
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        logger.debug(
            "COMMAND[{}]: {} -- {}".format(
                e.returncode, command, e.output.decode("utf-8", "ignore").strip()
            )
        )
        return "version not available"

    # success:
    version = result.decode("utf-8", "ignore").strip()
    logger.debug("COMMAND[0]: ({}) -- result({})".format(command, version))
    return version


def populate_subproc_version(subproc_id, subproc_conf):
    """collects subproc version as subprocs are requested."""

    global subproc_version
    if subproc_version is None:
        subproc_version = {}
    if subproc_id not in subproc_version:
        subproc_version[subproc_id] = get_subproc_version(subproc_conf["wrapper_path"])


def render_error(request, subproc_id=None, msgs=[], status_code=500):
    global subproc_version
    subproc_name = "app n/a"
    subproc_v = "version n/a"
    if subproc_id:
        subproc_conf = settings.HXARC_SUBPROCS[subproc_id]
        subproc_name = subproc_conf["display_name"]
        subproc_v = subproc_version[subproc_id]

    return render(
        request,
        "upload/error.html",
        {
            "hxarc_version": hxarc_version,
            "hxarc_subprocs": settings.HXARC_SUBPROCS,
            "subproc_name": subproc_name,
            "subproc_version": subproc_v,
            "errors": msgs,
        },
        status=status_code,
    )


def prepare_django_request(request):
    result = {
        "https": "on" if request.is_secure() else "off",
        "http_host": request.META["HTTP_X_FORWARDED-FOR"] \
            if "HTTP_X_FORWARDED-FOR" in request.META else request.META["HTTP_HOST"],
        "script_name": request.META["PATH_INFO"],
        "get_data": request.GET.copy(),
        "post_data": request.POST.copy(),
    }
    return result


@csrf_exempt
def saml(request):
    """handles saml2 acs and slo endpoints."""

    req = prepare_django_request(request)
    auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)

    # request logout to hkey
    if "slo" in req["get_data"]:
        name_id = request.session.get("samlNameId", None)
        session_index = request.session.get("samlSessionIndex", None)
        name_id_format = request.session.get("samlNameIdFormat", None)
        name_id_nq = request.session.get("samlNameIdNameQualifier", None)
        name_id_spnq = request.session.get("samlNameIdSPNameQualifier", None)

        # log user out!
        logout(request)

        return HttpResponseRedirect(
            auth.logout(
                name_id=name_id,
                name_id_format=name_id_format,
                session_index=session_index,
                nq=name_id_nq,
                spnq=name_id_spnq,
            )
        )
    # login callback
    elif "acs" in req["get_data"]:
        auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
        auth.process_response()
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()

        if not errors:
            if "AuthNRequestID" in request.session:
                del request.session["AuthNRequestID"]
            request.session["samlUserdata"] = auth.get_attributes()
            request.session["samlNameId"] = auth.get_nameid()
            request.session["samlSessionIndex"] = auth.get_session_index()

            # each attribute comes as a list!
            username = request.session["samlUserdata"][settings.SAML_USERNAME_ATTR][0]
            hxarc_login_user(request, username)

            if "RelayState" in req["post_data"] \
                and \
                OneLogin_Saml2_Utils.get_self_url(req) != req["post_data"]["RelayState"]:
                    return HttpResponseRedirect(
                            auth.redirect_to(req["post_data"]["RelayState"])
                    )
            else:
                return upload_landing(request)

        else:
            error_reason = auth.get_last_error_reason()
            emsg = "errors: {}, error_reason: {}, not_auth_warn: {}".format(
                errors, error_reason, not_auth_warn
            )
            logger.error(emsg)
            if auth.get_settings().is_debug_active():
                raise Exception(emsg)
            else:
                return render_error(
                    request,
                    msgs=[emsg],
                    status_code=400,
                )
    else:
        logger.error("saml2 unknown request({})".format(req["get_data"]))
        raise HttpResponseNotFound()


def hkey_upload(request):
    """auth for hxarc upload

    enforces authentication via hkey
    dispatches the requested page to proper app
    - expects that page starts with app name; e.g kondo_projects
    """
    req = prepare_django_request(request)

    if not request.user.is_authenticated:
        auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
        return_to = "{}/".format(OneLogin_Saml2_Utils.get_self_url(req))
        return HttpResponseRedirect(auth.login(return_to))
    else:
        return upload_landing(request)


def hxarc_login_user(request, username):
    # create/login user here!
    UserModel = get_user_model()
    user, created = UserModel._default_manager.get_or_create(username=username)
    if created:  # make sure new users cannot login via admin ui
        user.set_unusable_password()
        user.is_staff = False
        user.is_superuser = False
        user.save()
    login(request, user)


