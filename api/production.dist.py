# This file overwrites some of the options in settings.py, to ensure a secure production environment
# You can make changes to this file, if you want to change some settings for Production.
# Confideral information should not be uploaded to VCS and will be added only on the production server
# Please Raise an exception on options, where the value should be changed but works when unchanged
# Also see https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/
import os

DEBUG = False

SECRET_KEY = None  # Automatically raises exception if missing

ALLOWED_HOSTS = ['api.wildfyre.net', ]


# Admins
# https://docs.djangoproject.com/en/1.10/ref/settings/#admins

ADMINS = [('Info-Screen Webmaster', 'webmaster@Info-Screen.me')]


# Logging
# https://docs.djangoproject.com/en/1.10/ref/settings/#logging

LOG_BASE_PATH = '/var/log/api/'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s:%(lineno)d ~ %(message)s'
        },
    },
    'handlers': {
        'fileInfo': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': LOG_BASE_PATH + 'info.log',
        },
        'fileWarning': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': LOG_BASE_PATH + 'warning.log',
        },
        'fileError': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': LOG_BASE_PATH + '/error.log',
        },
    },
    'root': {
        'handlers': ['fileInfo', 'fileWarning', 'fileError', ],
        'level': 'INFO',
    },
}


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'api',
        'USER': 'api',
        'PASSWORD': '',  # Set password
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}


# E-Mail
# https://docs.djangoproject.com/en/1.10/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.wildfyre.net'
EMAIL_PORT = '587'  # Use submission Port
EMAIL_HOST_USER = 'noreply@wildfyre.net'
EMAIL_HOST_PASSWORD = ''  # Set password
EMAIL_USE_TLS = True

EMAIL_SUBJECT_PREFIX = '[WildFyre] '
DEFAULT_FROM_EMAIL = 'noreply@wildfyre.net'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = '/var/www/static/api'
STATIC_URL = 'https://static.wildfyre.net/api/'

MEDIA_ROOT = '/var/www/upload/api'
MEDIA_URL = 'https://upload.wildfyre.net/api/'


# Security Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
