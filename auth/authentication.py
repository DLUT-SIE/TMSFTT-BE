'''Authentication classes for JWT.'''
from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import (
    get_authorization_header
)
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

from rest_framework_jwt.settings import api_settings


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj

    This version disables authentication with cookie by checking
    `settings.JWT_AUTH_COOKIE` instead of `api_settings.JWT_AUTH_COOKIE`,
    so the `api_settings.JWT_AUTH_COOKIE` will remains True so that our clients
    can get cookies correctly. If `request.path` starts with any routes listed
    in `settings.JWT_AUTH_COOKIE_WHITELIST` then cookie authentication will be
    permitted.
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        '''Try to authenticate user.'''
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        # If request.path matches any routes listed in
        # settings.JWT_AUTH_COOKIE_WHITELIST, then cookie-based authentication
        # will be permitted.
        if not auth and any(
                request.path.startswith(x)
                for x in settings.JWT_AUTH_COOKIE_WHITELIST):
            return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)

        if not auth:
            if settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(
            api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)
