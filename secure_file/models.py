'''Define ORM models for secure_file module.'''
from django.db import models
from django.contrib.auth import get_user_model
from django.core.files import File
from rest_framework import response, status

from auth.services import PermissonsService
from secure_file.utils import (
    get_full_encrypted_file_download_url, get_full_plain_file_download_url)


User = get_user_model()


class FileFromPathMixin:
    '''Provide function to generate instance from given file target.'''
    @classmethod
    def from_path(cls, user, fname, target):
        '''Create SecureFile from given path.

        Paramters
        ---------
        user: User
            The user who creates this file.
        fname: str
            The name of the file.
        target: str or InMemoryFile
            The path of the file or an InMemoryFile object.

        Return
        ------
        secure_file: SecureFile
            The created SecureFile instance.
        '''
        if isinstance(target, str):
            secure_file = cls(user=user)
            with open(target, 'rb') as handle:
                secure_file.path.save(fname, File(handle), save=True)
            return secure_file
        return cls.objects.create(user=user, path=target)


class SecureFile(FileFromPathMixin, models.Model):
    '''Provide authentication for system generated files.'''
    GENERATE_FILE_SRC_SEP = ':'
    GENERATE_FILE_SRC_PREFIX = 'system-generated'

    class Meta:
        verbose_name = '安全文件'
        verbose_name_plural = '安全文件'
        default_permissions = ()
        permissions = (
            ('download_file', '文件的下载权限'),
        )

    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    user = models.ForeignKey(User, verbose_name='操作人',
                             blank=True, null=True,
                             on_delete=models.PROTECT)
    path = models.FileField(verbose_name='文件路径',
                            upload_to='secure-files/%Y/%m/%d')

    @classmethod
    def from_path(cls, user, fname, target):
        secure_file = super().from_path(user, fname, target)
        PermissonsService.assigin_object_permissions(user, secure_file)
        return secure_file

    def generate_download_response(self, request):
        '''Generate secured HTTP response for downloading this file.

        This method is usuallly one-time only, called right the creation of
        the instance.

        Parameters
        ----------
        request: Request
            The request is used to determine the domain and port for current
            site.

        Return
        ------
        response: Response
            The json response contains only one key named 'url', this full url
            points to the real file created.
        '''
        url = get_full_encrypted_file_download_url(
            request, type(self), 'path', self.path.name, 'download_file'
        )
        return response.Response({'url': url}, status=status.HTTP_201_CREATED)


class InSecureFile(FileFromPathMixin, models.Model):
    '''
    Provide direct acccees to files, these files are untrusted and publicly
    accessible.
    '''
    class Meta:
        verbose_name = '不安全文件'
        verbose_name_plural = '不安全文件'
        default_permissions = ()

    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    user = models.ForeignKey(User, verbose_name='操作人',
                             blank=True, null=True,
                             on_delete=models.PROTECT)
    path = models.FileField(verbose_name='文件路径',
                            upload_to='insecure-files/%Y/%m/%d')

    def generate_download_response(self, request):
        '''Generate HTTP response for downloading this file.

        This method is usuallly one-time only, called right the creation of
        the instance.

        Parameters
        ----------
        request: Request
            The request is used to determine the domain and port for current
            site.

        Return
        ------
        response: Response
            The json response contains only one key named 'url', this full url
            points to the real file created.
        '''
        url = get_full_plain_file_download_url(request, str(self.pk))
        return response.Response({'url': url}, status=status.HTTP_201_CREATED)
