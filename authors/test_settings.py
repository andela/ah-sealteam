import os
from authors.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DATABASE'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('PASSWORD'),
        'HOST': 'localhost',
        'PORT': 5432
    }
}