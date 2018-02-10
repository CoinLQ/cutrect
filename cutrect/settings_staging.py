from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cutrect_stage',
        'USER': 'lqzj',
        'PASSWORD': 'lqdzjsql',
        'HOST': '127.0.0.1',
        'PORT': '5432',

    },
}

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'polling_interval': 3,
    'region': 'cn-north-1',
    'visibility_timeout': 3600,
    'queue_name_prefix': 'lq-stage-'
}
