'''Provide utility functions for secure_file module.'''
import os.path as osp
from urllib.parse import urljoin, urlencode, urlsplit, parse_qs
from collections import OrderedDict

from django.conf import settings

from infra.utils import dev_logger, encrypt, decrypt, get_full_url


def encrypt_file_download_url(
        model_class, field_name, file_path, perm_name=None):
    '''Encrypt file download url.

    Parameters
    ----------
    model_class: models.Model
        The class of the model owning the `FileField` for the file.
    field_name: str
        The name of the `FileField` on `model_class`.
    file_path: str
        The true path of the file, usually the name of the `FieldFile`.
    perm_name: str
        The name of the permission, the corresponding permission will be
        checked during file download request.

    Return
    ------
    encrypted_file_url: string
        Encrypted file download url. Access this URL with appropriate
        permissions will be responded with the real file data.
    '''
    model_name = (
        f'{model_class._meta.app_label}.{model_class._meta.object_name}'
    )

    query_params = OrderedDict([
        ('model_name', model_name),
        ('field', field_name),
    ])
    if perm_name is not None:
        query_params['perm'] = perm_name

    path = f'{file_path}?{urlencode(query_params)}'
    path = encrypt(path)
    path = urljoin(settings.MEDIA_URL, path)
    return path


def decrypt_file_download_url(encrypted_url):
    '''Decrypt necessary arguments from encrypted url.

    Paramter
    --------
    encrypted_url: str
        The encrypted url.

    Returns
    -------
    model_name: str
        The name of the model to which the file related.
    field_name: str
        The name of the FileField on the model.
    path: str
        The content path of the FileField.
    perm_name: str
        The object permission needed to download the file.
    '''
    path = decrypt(encrypted_url)
    split_result = urlsplit(path)
    path = split_result.path
    query_params = parse_qs(split_result.query)
    model_name = query_params.get('model_name', [None])[0]
    if model_name is None:
        dev_logger.info('参数无效')
        raise ValueError('参数无效')
    field_name = query_params.get('field', ['path'])[0]
    perm_name = query_params.get('perm', ['download_file'])[0]
    return model_name, field_name, path, perm_name


def get_full_encrypted_file_download_url(
        request, model_class, field_name, file_path, perm_name=None):
    '''
    A helper function for generating full URL for downloading encrypted
    file.

    Parameters
    ----------
    request: Request
        The original request object.
    model_class: models.Model
        The class of the model owning the `FileField` for the file.
    field_name: str
        The name of the `FileField` on `model_class`.
    file_path: str
        The true path of the file, usually the name of the `FieldFile`.
    perm_name: str
        The name of the permission, the corresponding permission will be
        checked during file download request.

    Returns
    -------
    url: str
        The full URL for downloading encrypted file.
    '''
    encrypted_url = encrypt_file_download_url(
        model_class, field_name, file_path, perm_name)
    return get_full_url(request, encrypted_url)


def infer_content_type(fname):
    '''Infer content type from extension name.'''
    content_types = {
        '.xlsx': ('application/vnd.openxmlformats-officedocument'
                  '.spreadsheetml.sheet'),
        '.xls': 'application/vnd.ms-excel',
        '.csv': 'text/csv',
        '.png': 'image/png',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpg',
    }
    ext = osp.splitext(fname.lower())[-1]
    return content_types.get(ext, 'text/plain')
