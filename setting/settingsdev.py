from .settings import *

# DEBUG=False 不会用自带的 server 去 server js/css 等静态文件
# 需要用 nginx 之类的去做静态文件的 server.
DEBUG = True
INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS += INTERNAL_IPS
ALLOWED_HOSTS.append('localhost')

# 重置 setting 里的 STATIC_ROOT 配置
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# static 目录配置
# 如果 DEBUG 为 False 这里就会失效，需要用 NGIX 代理
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
    os.path.join(PROJECT_ROOT, 'frontend/dist/static'),
]

# 开发环境开启跨域
CORS_ORIGIN_ALLOW_ALL = True

#INSTALLED_APPS.append('debug_toolbar')
#MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# 请按照你开发时本机的数据库名字，密码，端口填写

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'polling_interval': 3,
    'region': 'cn-north-1',
    'visibility_timeout': 3600,
    'queue_name_prefix': 'lq-dev-'
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cutrect_local',
        'USER': 'lqzj',
        'PASSWORD': 'lqdzjsql',
        'HOST': 'www.dzj3000.com',
        'PORT': '5432',

    },
}
