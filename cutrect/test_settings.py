from .settings import *

# DEBUG=False 不会用自带的 server 去 server js/css 等静态文件
# 需要用 nginx 之类的去做静态文件的 server.
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cutrect_local',
        'USER': 'lqzj',
        'PASSWORD': 'lqdzjsql',
        'HOST': '127.0.0.1',
        'PORT': '5432',

    },
}