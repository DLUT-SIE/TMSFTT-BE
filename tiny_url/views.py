'''Provide API views for tiny_url module.'''
from django.shortcuts import get_object_or_404, redirect

from tiny_url.models import TinyURL


def redirect_url(request, short_url):
    '''redirect to long_url.'''
    tiny_url = get_object_or_404(TinyURL, short_url=short_url)

    return redirect(tiny_url)
