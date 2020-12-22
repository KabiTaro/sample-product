from core.settings import *
import dj_database_url
from conoha.service import ConohaObjectStorage as cos

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'local_db',
        'USER': 'back_user',
        'PASSWORD': 'e54fsf523',
        'HOST': 'db',
        'POST': 3306
    },
}

db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)

DATABASES['default'].update(db_from_env)

# 開発環境で画像を格納するコンテナ
IMAGE_CONTAINER = cos.factory(container_name='dev_container')
