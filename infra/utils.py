'''Provide useful utilities shared among modules.'''
import os.path as osp
import hashlib

from django.utils.deconstruct import deconstructible
from django.utils import timezone


@deconstructible
class CustomHashPath:
    '''Append hash fingerprint to filename of the uploaded file.

    Multiple uploading will not replace the file with the same filename. Files
    uploaded by the user that has same content and same filename will be saved
    as one copy.

    :Author:
        Youchen <youchen.du@gmail.com>

    Parameters
    ----------
    base: str
        The base directory name.
        Default: *uploads*
    by_date: bool
        Whether to use current date in the path, e.g. *uploads/2019/01/01/*.
        Default: True.
    by_user: bool
        Whether to use current user in the path, e.g. *uploads/user_<id>/*.
        Default: True.
    '''
    def __init__(self, base='uploads', by_date=True, by_user=True):
        self.base = base
        self.by_date = by_date
        self.by_user = by_user
        path_format = '{base}'
        if self.by_date:
            path_format = osp.join(path_format, '{date}')
        if self.by_user:
            path_format = osp.join(path_format, 'user_{user}')
        self.path_format = osp.join(path_format, '{fname}_{fingerprint}.{ext}')

    def __eq__(self, other):
        return (self.base == other.base
                and self.by_date == other.by_date
                and self.by_user == other.by_user
                and self.path_format == other.path_format)

    def __call__(self, instance, filename):
        # Calculate fingerprint
        hasher = hashlib.md5()
        instance.path.open()
        hasher.update(instance.path.read())
        instance.path.close()
        fingerprint = hasher.hexdigest()

        fname, ext = osp.splitext(filename)

        date = timezone.now().strftime('%Y/%m/%d')

        # Format the path, unused variables will be discarded.
        path = self.path_format.format(
            base=self.base,
            date=date,
            user=instance.user.id,
            fname=fname,
            fingerprint=fingerprint,
            ext=ext)
        return path
