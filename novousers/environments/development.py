DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '3.217.72.41', 'usuarios.nnco.cloud']

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

SITE_URL = 'http://3.217.72.41'
