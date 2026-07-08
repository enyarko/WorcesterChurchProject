DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}





DEBUG = False

ALLOWED_HOSTS = [
    "worcesterchurchapp-env.eba-ca2fp3t2.us-east-1.elasticbeanstalk.com",
]

CSRF_TRUSTED_ORIGINS = [
    "http://worcesterchurchapp-env.eba-ca2fp3t2.us-east-1.elasticbeanstalk.com",
]
