import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from os import environ
from conoha.service import ConohaObjectStorage as cos

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 本来であれば秘密情報として扱い、Secretsから受け渡すべし
# SECRET_KEY = environ.get('SECRET_KEY')
SECRET_KEY = 'jzo5j$!-sg0wz($+k3&0g$ws&bdo4&9me05()j666%2h7zsk-q'

# カバレッジ計測用のhtml格納コンテナ
COVERAGE_CONTAINER = 'coverage'

DEBUG = False

ALLOWED_HOSTS = [environ.get('PRODUCTION_IP')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # サードパーティ
    'rest_framework',
    # 自作アプリ
    'api_v1.apps.ApiV1Config',
    'conoha.apps.ConohaConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': environ.get('CONOHA_DB_NAME'),
        'USER': environ.get('CONOHA_DB_USER_NAME'),
        'PASSWORD': environ.get('CONOHA_DB_PASSWORD'),
        'HOST': environ.get('CONOHA_DB_HOST'),
        'POST': 3306,
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.AutoSchema',
    'DATETIME_FORMAT': '%Y/%m/%d %H:%M:%S',
    'DATETIME_INPUT_FORMATS': ['%Y/%m/%d %H:%M:%S', 'iso-8601'],
    'DATE_FORMAT': '%Y/%m/%d',
    'DATE_INPUT_FORMATS': ['%Y/%m/%d', 'iso-8601'],
    'TIME_FORMAT': '%H:%M',
    'TIME_INPUT_FORMATS': ['iso-8601']
}

# dsnを省略した場合は環境変数SENTRY_DSNから値を読み込まれる(SENTRY_DSNが空の場合は追跡情報が送信されない)
# environmentを省略した場合は環境変数SENTRY_ENVIRONMENTから値を読み込まれる
# environmentは以下の3つ
# test(CIジョブで実行されるユニットテスト時の環境),development(開発環境),production (本番環境)
# https://docs.sentry.io/platforms/python/guides/django/configuration/options/
sentry_sdk.init(
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
    
# 本番環境で画像を格納するコンテナ
IMAGE_CONTAINER = cos.factory(container_name='prd_container')
