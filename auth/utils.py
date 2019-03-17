'''Utility functions provided by auth module.'''
import hashlib

from django.conf import settings

from auth.serializers import UserSerializer


def get_user_secret_key(user):
    '''Generate a secret key for a user.

    We format the unhashed_key by including the time the module was imported.
    This way we can invalidate all tokens when the server is restart to ensure
    security.
    '''
    unhashed_key = '{}.{}'.format(
        settings.SECRET_KEY,  # Django secret key
        user.password,  # User password
        ).encode()
    sha1 = hashlib.new('sha1')
    sha1.update(unhashed_key)
    secret_key = sha1.hexdigest()
    return secret_key


def jwt_response_payload_handler(token, user=None, request=None):
    """Returns the response data for both the login and refresh views."""
    return {
        'user': UserSerializer(user).data,
        'token': token
    }
