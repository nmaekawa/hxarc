import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.views.decorators.csrf import csrf_exempt
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings


class HkeySaml:
    """saml2 config for python3-saml.

    keeps saml settings in class and don't read from file every login
    """

    __settings = {}

    @classmethod
    def get_auth(cls, req):
        if not cls.__settings:
            a = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
            cls.__settings = a.get_settings()
        else:
            a = OneLogin_Saml2_Auth(req, old_settings=cls.__settings)
        return a

    @classmethod
    def get_sp_metadata(cls):
        if not cls.__settings:
            cls.__settings = OneLogin_Saml2_Settings(
                settings=None,
                custom_base_path=settings.SAML_FOLDER,
            )
        metadata = cls.__settings.get_sp_metadata()
        errors = cls.__settings.validate_metadata(metadata)
        return (metadata, errors)


@csrf_exempt
def metadata(request):
    """saml2 metadata endpoint.

    displays what is configured in SAML_FOLDER/settings.py
    """
    metadata, errors = HkeySaml.get_sp_metadata()
    if len(errors) == 0:
        resp = HttpResponse(content=metadata, content_type="text/xml")
    else:
        resp = HttpResponseServerError(content=", ".join(errors).encode("utf-8"))
    return resp


def hkey_index(request, **kwargs):
    """hkey landing view, enforces hkey auth to the service landing page

    Expects "service_view" in kwargs: view function to serve this request, once the user is authenticated.
    In urls.py, it would be something like:
        path("myapp/<int:year>", hkey.views.hkey_index, {"service_view": myapp.views.landing_view})
    """
    service_view = kwargs.get("service_view", None)
    if service_view is None:  # all calls are going to fail if this is not set!!!!
        return HttpResponseServerError(
            content="unable to find service_view to return".encode("utf-8")
        )

    req = prepare_django_request(request)
    if not request.user.is_authenticated:
        auth = HkeySaml.get_auth(req)
        return_to = request.get_full_path()
        return HttpResponseRedirect(auth.login(return_to))
    else:
        del kwargs["service_view"]
        return service_view(request, *kwargs)


@csrf_exempt
def saml(request, **kwargs):
    """handles saml2 acs and slo endpoints.

    see hkey_index() comment for how to set arg "service_view"
    """
    service_view = kwargs.get("service_view", None)
    if service_view is None:  # all calls are going to fail if this is not set!!!!
        return HttpResponseServerError(
            content="unable to find service_view to return".encode("utf-8")
        )

    req = prepare_django_request(request)
    auth = HkeySaml.get_auth(req)

    # request logout to hkey
    if "slo" in req["get_data"]:
        name_id = request.session.get("samlNameId", None)
        session_index = request.session.get("samlSessionIndex", None)
        name_id_format = request.session.get("samlNameIdFormat", None)
        name_id_nq = request.session.get("samlNameIdNameQualifier", None)
        name_id_spnq = request.session.get("samlNameIdSPNameQualifier", None)

        # logout from django app
        django_logout(request)

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
            service_login_user(request, username)

            if (
                "RelayState" in req["post_data"]
                and request.get_full_path() != req["post_data"]["RelayState"]
            ):
                return HttpResponseRedirect(
                    auth.redirect_to(req["post_data"]["RelayState"])
                )
            else:
                # return landing page
                del kwargs["service_view"]
                return service_view(request, *kwargs)
        else:
            error_reason = auth.get_last_error_reason()
            msg = "errors: {}, error_reason: {}, not_auth_warn: {}".format(
                errors, error_reason, not_auth_warn
            )
            logging.getLogger(__name__).error(msg)
            if auth.get_settings().is_debug_active():
                raise Exception(msg)
            else:
                return HttpResponseNotFound(
                    "errors: {}, error_reason: {}, not_auth_warn: {}".format(
                        errors, error_reason, not_auth_warn
                    )
                )
    else:
        logging.getLogger(__name__).error(
            "saml2 unknown request({})".format(req["get_data"])
        )
        return HttpResponseNotFound()


def service_login_user(request, username):
    """get or create user, then logs them in."""
    UserModel = get_user_model()
    user, created = UserModel._default_manager.get_or_create(username=username)
    if created:  # ensure new users cannot login via admin ui
        user.set_unusable_password()
        user.is_staff = False
        user.is_superuser = False
        user.save()
    django_login(request, user)


def prepare_django_request(request):
    result = {
        "https": "on" if request.is_secure() else "off",
        "http_host": (
            request.META["HTTP_X_FORWARDED-FOR"]
            if "HTTP_X_FORWARDED-FOR" in request.META
            else request.META["HTTP_HOST"]
        ),
        "script_name": request.META["PATH_INFO"],
        "get_data": request.GET.copy(),
        "post_data": request.POST.copy(),
    }
    return result
