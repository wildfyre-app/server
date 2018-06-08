# This file overwrites some of the options in settings.py, to ensure a secure production environment
# You can make changes to this file, if you want to change some settings for Production.
# Confideral information should not be uploaded to VCS and will be added only on the production server
# Please Raise an exception on options, where the value should be changed but works when unchanged
# Also see https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/
import os


# Ensure settings were ajusted
if os.environ.get('SETUP') is None:
    raise NotImplementedError("Configuration required. Check production.dist.py")


DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')  # Automatically raises exception if missing

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST', 'api.wildfyre.net'), ]


# Admins
# https://docs.djangoproject.com/en/1.10/ref/settings/#admins

ADMINS = [('Info-Screen Webmaster', 'webmaster@Info-Screen.me')]


# Logging
# https://docs.djangoproject.com/en/1.10/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] [%(process)s] [%(levelname)s] %(name)s:%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %z'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'formatter': 'default',
        },
    },
    'loggers': {
        # Override the default, it will be handled by the root logger
        'django': {},
        'django.server': {},
    },
    'root': {
        'handlers': ['console', ],
    }
}

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'api'),
        'USER': os.environ.get('DB_USER', 'api'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}


# E-Mail
# https://docs.djangoproject.com/en/1.10/topics/email/

EMAIL_BACKEND = os.environ['EMAIL_BACKEND']
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '587')  # Use submission Port
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

EMAIL_SUBJECT_PREFIX = '[WildFyre] '
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@wildfyre.net')


# reCAPTCHA secret key
# https://www.google.com/recaptcha/admin

RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET', '')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.environ.get('STATIC_ROOT', '/data/static')
STATIC_URL = os.environ['STATIC_URL']

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/data/media')
MEDIA_URL = os.environ['MEDIA_URL']


# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'


# Proxy Settings
USE_X_FORWARDED_PORT = True
