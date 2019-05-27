'''Provide utility functions for secure_file module.'''
import os.path as osp
from urllib.parse import urlencode, urlsplit, parse_qs, quote
from collections import OrderedDict

from django.conf import settings
from django.http import HttpResponse
from rest_framework import exceptions

from infra.utils import prod_logger, dev_logger, encrypt, decrypt, get_full_url
from secure_file import SECURE_FILE_PREFIX, INSECURE_FILE_PREFIX


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
    path = osp.join(SECURE_FILE_PREFIX, path)
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
    perm_name = query_params.get('perm', ['view_securefile'])[0]
    return model_name, field_name, path, perm_name


def get_full_plain_file_download_url(request, path):
    '''
    A helper function for generating full URL for downloading insecure files.
    '''
    path = osp.join(INSECURE_FILE_PREFIX, path)
    return get_full_url(request, path)


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


def populate_file_content(resp, field_file):
    '''Populate file content for HTTP response.

    If settings.DEBUG is False, then we ask Nginx to serve the file.
    '''
    if settings.DEBUG:
        try:
            resp.content = field_file.read()
        except Exception as exc:
            msg = f'读取文件失败: {exc}'
            dev_logger.info(msg)
            raise exceptions.NotFound()
    else:
        resp['X-Accel-Redirect'] = (
            f'/protected-files/{quote(field_file.name)}'
        )


def generate_download_response(request, field_file, logging=True):
    '''Serve file from `field_file` for request.'''
    basename = osp.basename(field_file.name)
    if logging:
        msg = (
            f'用户 {request.user.first_name}'
            f'(用户名: {request.user.username}) '
            f'请求下载文件: {field_file.name}'
        )
        prod_logger.info(msg)
    resp = HttpResponse(content_type=infer_content_type(basename))
    resp['Content-Disposition'] = (
        f'attachment; filename={quote(basename)}'
    )
    populate_file_content(resp, field_file)
    return resp
