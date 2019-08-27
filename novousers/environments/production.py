from django.utils.log import DEFAULT_LOGGING

DEBUG = False
SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = ['usuarios.nnco.cloud']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'novousers',
        'USER': 'postgres',
        'PASSWORD': 'nauticadjango',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

SITE_URL = 'https://usuarios.nnco.cloud'

LOGGING = DEFAULT_LOGGING
LOGGING['handlers']['slack_admins'] = {
    'level': 'ERROR',
    'filters': ['require_debug_false'],
    'class': 'novousers.slack_logger.SlackExceptionHandler',
}
LOGGING['loggers']['django.security.DisallowedHost'] = {
    'handlers': [],
    'propagate': False,
}
LOGGING['loggers']['django'] = {
    'handlers': ['console', 'mail_admins', 'slack_admins'],
    'level': 'INFO',
}
