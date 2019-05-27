'''Provide useful utilities shared among modules.'''
import logging
import base64
from urllib.parse import urlunsplit

from Crypto import Random, Cipher, Hash
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.renderers import BrowsableAPIRenderer


dev_logger = logging.getLogger('django')  # pylint: disable=invalid-name
prod_logger = logging.getLogger('django.prod')  # pylint: disable=invalid-name


def positive_int(integer_string, strict=False, cutoff=None):
    '''Cast a string to a strictly positive integer.'''
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret


def format_file_size(size_in_bytes):
    '''Format human-readable file size.'''
    if size_in_bytes < 0 or size_in_bytes >= 1024**6:
        raise ValueError('参数超出转换范围')
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    val = size_in_bytes
    unit_idx = 0
    while val / 1024 > 1:
        unit_idx += 1
        val /= 1024
    return '{:.2f} {}'.format(val, units[unit_idx])


class BrowsableAPIRendererWithoutForms(
        BrowsableAPIRenderer):  # pragma: no cover
    """Renders the browsable api, but excludes the forms."""

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx['display_edit_forms'] = False
        return ctx

    def show_form_for_method(self, view, method, request, obj):
        """We never want to do this! So just return False."""
        return False

    def get_filter_form(self, data, view, request):
        return

    def get_rendered_html_form(self, data, view, method, request):
        """Why render _any_ forms at all. This method should return
        rendered HTML, so let's simply return an empty string.
        """
        return ''


def encrypt(value):
    '''Encrypt value with AES algorithm.

    Parameters
    ----------
    value: string
        The value needs to be encrypted.

    Return
    ------
    cipher_text: string
        The text been encrypted, format: <encrypted_text>|<iv>|<fp>
    '''
    hasher = Hash.SHA256.new()
    hasher.update(value.encode())
    fingerprint = hasher.digest()

    rndfile = Random.new()
    iv_data = rndfile.read(16)
    cipher = Cipher.AES.new(settings.SECRET_KEY[:32],
                            Cipher.AES.MODE_CFB, iv_data)
    encrypted = cipher.encrypt(value)
    parts = [encrypted, iv_data, fingerprint]
    return '|'.join(base64.urlsafe_b64encode(x).decode() for x in parts)


def decrypt(cipher_text):
    '''Decrypt value with AES algorithm.

    Paramters
    ---------
    cipher_text: string
        The text been encrypted, format: <encrypted_text>|<iv>|<fp>

    Return
    ------
    value: string
        The real value under the cipher_text.
    '''
    encrypted, iv_data, gt_fingerprint = [
        base64.urlsafe_b64decode(x.encode()) for x in cipher_text.split('|')]

    cipher = Cipher.AES.new(settings.SECRET_KEY[:32],
                            Cipher.AES.MODE_CFB, iv_data)
    value = cipher.decrypt(encrypted)

    hasher = Hash.SHA256.new()
    hasher.update(value)
    fingerprint = hasher.digest()
    if fingerprint != gt_fingerprint:
        raise ValueError('已被篡改的内容')
    return value.decode()


def get_full_url(request, path):
    '''Generate full URL path for request.

    For example, `/media/abccc` will be converted to full URL like
    `http://host:port/media/abccc`

    Parameters
    ----------
    request: Request
        The original request object.
    path: str
        Partial path.

    Return
    ------
    url: str
        A full URL for given path.
    '''
    current_site = get_current_site(request)
    return urlunsplit((
        request.scheme,  # URL scheme specifier
        current_site.domain,  # Network location part
        path,  # Hierarchical path
        '',  # Query component
        ''  # Fragment identifier
    ))
