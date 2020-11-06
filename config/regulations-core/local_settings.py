import os

DEBUG = True

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST'),]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.environ.get('DB_USER', 'eregs'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sgere'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'NAME': os.environ.get('DB_NAME', 'eregs'),
    }
}
