'''Provide services of TinyURL module.'''
import random

from tiny_url.models import TinyURL


class TinyURLService:
    '''Provide services for TinyURL.'''
    @staticmethod
    def generate_tiny_url(long_url):
        '''generate tiny url from long url.

        Parameters
        ----------
        long_url: string

        Returns
        -------
        tiny_url: TinyURL
        '''
        tiny_url = TinyURL.objects.filter(url=long_url)
        if tiny_url:
            return tiny_url[0]
        base62 = ('0123456789abcdefghijklmnopqrstuv'
                  'wxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        tiny_url = ''.join(random.choice(base62) for _ in range(6))
        return TinyURL.objects.create(url=long_url, short_url=tiny_url)
