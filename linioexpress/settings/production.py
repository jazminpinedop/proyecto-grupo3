from .base import *
import dj_database_url
DEBUG = config('DEBUG', cast=bool)
ALLOWED_HOSTS = ['grupo3linioexpress.herokuapp.com']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]

DATABASES = {
    'default': { 
        'ENGINE': 'django.db.backend.postgresql_psicopg2'
        'NAME': 'depka57av35ksr'
        'USER': 'eztrqipqsocmay'
        'PASSWORD': 'eaf1f0343394522d8e6c665c7f2a1f087dbd1f5960ffd5a5730db884847d28a0'
        'HOST': 'ec2-54-205-248-255.compute-1.amazonaws.com'
        'PORT': '5432'
    }
}



STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')