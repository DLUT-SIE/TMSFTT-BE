from django.conf import settings
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

from rest_framework_jwt.settings import api_settings


class SecureFileCookieAuthentication(BaseJSONWebTokenAuthentication):
    """Allow cookie-based authentication for secure files."""
    def get_jwt_value(self, request):
        '''Check request.path startswith any white list urls.'''
        if any(request.path.startswith(x)
               for x in settings.JWT_AUTH_COOKIE_WHITELIST):
            return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
        return None
