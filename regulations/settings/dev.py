from .base import *

DEBUG = True

CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
CACHES['eregs_longterm_cache']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
CACHES['api_cache']['TIMEOUT'] = 5  # roughly per request

ROOT_URLCONF = 'regulations.urls'

try:
    from local_settings import *
except ImportError:
    pass
