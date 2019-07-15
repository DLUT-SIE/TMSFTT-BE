'''Define ORM models for TinyURL'''
from django.db import models


class TinyURL(models.Model):
    '''TinyURL stores the tinyurl to longurl'''
    url = models.URLField()
    short_url = models.CharField(max_length=6, db_index=True, unique=True)

    def __str__(self):
        return 'short_url: {}'.format(self.short_url)

    def get_absolute_url(self):
        '''return true url'''
        return '/user/{}'.format(self.url)
