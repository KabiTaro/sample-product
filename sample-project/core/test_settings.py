from core.settings import *
import dj_database_url
from conoha.service import ConohaObjectStorage as cos

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=True)

DATABASES['default'].update(db_from_env)

# テスト用
IMAGE_CONTAINER = cos.factory(
    container_name='test_container',
    tenant_id='test999999999999999999999',
    user='gncu999999999',
    password='test_password'
)
