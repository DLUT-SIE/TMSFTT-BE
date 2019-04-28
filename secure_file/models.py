'''Define ORM models for secure_file module.'''
from django.db import models
from django.contrib.auth import get_user_model
from django.core.files import File
from rest_framework import response, status

from secure_file.utils import encrypt_file_download_url


User = get_user_model()


class SecureFile(models.Model):
    '''Provide authentication for system generated files.'''
    GENERATE_FILE_SRC_SEP = ':'
    GENERATE_FILE_SRC_PREFIX = 'system-generated'

    class Meta:
        verbose_name = '受保护文件'
        verbose_name_plural = '受保护文件'
        default_permissions = ()
        permissions = (
            ('download_file', '拥有院系其他成员生成文件的下载权限'),
        )

    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    user = models.ForeignKey(User, verbose_name='操作人',
                             blank=True, null=True,
                             on_delete=models.PROTECT)
    path = models.FileField(verbose_name='文件路径',
                            upload_to='generated-files/%Y/%m/%d')

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

    def generate_secured_download_response(self):
        '''Generate secured HTTP redirect response for downloading this file.

        Return
        ------
        response: Response
            The json response contains only one key named 'url', this url
            points to the real file created.
        '''
        return response.Response({
            'url': encrypt_file_download_url(
                type(self), 'path', self.path.name, 'download_file')
        }, status=status.HTTP_201_CREATED)
