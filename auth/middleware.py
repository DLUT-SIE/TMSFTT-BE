'''Middlewares provided by auth module.'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from rest_framework_jwt.settings import api_settings


User = get_user_model()


# pylint: disable=R0903,C0111,R0201
class JWTAuthenticationMiddleware(MiddlewareMixin):
    '''Authenticate user by JWT.

    This middleware is used to replace the default AuthenticationMiddleware
    provided by Django.
    '''

    # pylint: disable=W0212
    @staticmethod
    def _get_user(request, jwt_payload):
        if not hasattr(request, '_jwt_cached_user'):
            try:
                user_id = int(jwt_payload.get('user_id', '-1'))
                request._jwt_cached_user = User.objects.get(id=user_id)
            except Exception:  # pylint: disable=W0703
                request._jwt_cached_user = AnonymousUser()
        return request._jwt_cached_user

    def _get_token(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
        authorization = dict(zip(authorization[::2], authorization[1::2]))
        token = authorization.get(api_settings.JWT_AUTH_HEADER_PREFIX,
                                  None)
        if token is None:
            token = request.COOKIES.get(api_settings.JWT_AUTH_COOKIE, None)

        return token

    def process_request(self, request):
        '''Set request.user if token is valid.'''
        if hasattr(request, 'user') and not request.user.is_anonymous:
            return
        token = self._get_token(request)
        try:
            jwt_payload = api_settings.JWT_DECODE_HANDLER(token)
        except Exception:  # pylint: disable=W0703
            jwt_payload = {'user_id': '-1'}
        request.user = SimpleLazyObject(
            lambda: self._get_user(request, jwt_payload))
