'''Utility functions provided by auth module.'''
import hashlib

from django.conf import settings
from django.utils.timezone import now


# The time when this module was imported
__MODULE_IMPORT_TIME = now()


def get_user_secret_key(user):
    '''Generate a secret key for a user.

    We format the unhashed_key by including the time the module was imported.
    This way we can invalidate all tokens when the server is restart to ensure
    security.
    '''
    unhashed_key = '{}.{}.{}'.format(settings.SECRET_KEY, user.id,
                                     __MODULE_IMPORT_TIME).encode()
    sha1 = hashlib.new('sha1')
    sha1.update(unhashed_key)
    secret_key = sha1.hexdigest()
    return secret_key
