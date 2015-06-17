"""
Django settings for demo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account', 
    'django.contrib.admin',
    'login',
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'demo.urls'

WSGI_APPLICATION = 'demo.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'login.auth.DemoBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS':{
            'read_default_file':os.path.join(BASE_DIR, 'mysql.conf')
            }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'static'),
)

# TYPEDEF

TYPE_CODE={
        'douban':1,
        'weibo':2,
        'qq':3,
        }

# KEY,SECRET

WEIBO_KEY = ''
WEIBO_SECRET = ''
# WEIBO_REDIRECT = 'http://192.168.172.128/login/weibo/complete/'
WEIBO_REDIRECT = 'http://demo.retoohs.com/login/weibo/complete/'
QQ_KEY = ''
QQ_SECRET = ''
#QQ_REDIRECT = 'http://192.168.172.128/login/qq/complete'
QQ_REDIRECT = 'http://demo.retoohs.com/login/qq/complete/'
DOUBAN_KEY = ''
DOUBAN_SECRET = ''
#DOUBAN_REDIRECT = 'http://192.168.172.128/login/douban/complete'
DOUBAN_REDIRECT = 'http://demo.retoohs.com/login/douban/complete/'

# TEMPLATES

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)
