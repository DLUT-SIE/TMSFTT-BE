'''Utility functions.'''
import hashlib
from urllib.parse import quote

from django.core.cache import cache
from django.utils.encoding import uri_to_iri, force_bytes

from drf_cache import (
    CACHE_KEY_FORMAT, INVERTED_INDEX_KEY_FORMAT, VARY_HEADERS
)


def build_cache_key(request, app_label, model_name, vary_headers=VARY_HEADERS):
    '''Construct cache key of the given request.'''
    uri = quote(uri_to_iri(request.build_absolute_uri()))
    vary = ''
    for vary_header in vary_headers:
        if vary_header in request.headers:
            vary += request.headers[vary_header]
    finger_print = hashlib.md5(force_bytes(vary)).hexdigest()
    data = {
        'method': request.method,
        'app_label': app_label,
        'model_name': model_name,
        'uri': uri,
        'fp': finger_print,
    }
    cache_key = CACHE_KEY_FORMAT.format(**data)
    return cache_key


def invalidate_all_caches(*_, **__):
    '''Invalidate all daches is a high-cost task, ideally we can only
    invalidate caches related to the model change, but it's not easy,
    so currently we invalidate all caches.
    '''
    cache.clear()


def build_key_for_instance_inverted_index(instance_id, app_label, model_name):
    '''Construct cache key for inverted index of the instance.'''
    data = {
        'app_label': app_label,
        'model_name': model_name,
        'instance_id': instance_id,
    }
    return INVERTED_INDEX_KEY_FORMAT.format(**data)
