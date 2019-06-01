'''Constants used in this module.'''


CACHE_NAME = 'default'
CACHE_TIMEOUT = 30 * 60
CACHE_KEY_FORMAT = (
    'DRF_CACHE:CACHE_KEY:{method}:{app_label}:{model_name}:{uri}:{fp}'
)
INVERTED_INDEX_KEY_FORMAT = (
    'DRF_CACHE:INVERTED_INDEX:{app_label}:{model_name}:{instance_id}'
)
VARY_HEADERS = ('Cookie', 'Authorization')
