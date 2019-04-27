'''Provide DRF fields for secure_file module.'''
import os.path as osp
from rest_framework import fields

from secure_file.utils import encrypt_file_download_url


class SecureFileField(fields.FileField):
    '''
    Provide similar functionalties with FileField but with secured file url.

    The FileField is encoded into:
      {
          'name': <file name>,
          'url': <encrypted download path>,
      }
    '''
    def __init__(self, *args, perm_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.perm_name = perm_name

    def to_representation(self, value):
        if not value:
            return None
        return {
            'name': osp.basename(value.name),
            'url': encrypt_file_download_url(
                value.field.model, self.source, value.name, self.perm_name)
        }
