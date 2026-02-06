# DEV
from .common import *
from datetime import timedelta

import os
import environ

env = environ.Env()
environ.Env.read_env()

HOST_IP = env('HOST_IP')
FRONTEND_URL = env('FRONTEND_URL')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ('django-insecure-x1a#yw-&_gh&jvp06gn)m2x-d@_z06ghuygo$^!f5s8g+)_mql')

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1), # This is for development
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'hZBVwFTiEsVWavJqGiP2VCIdVUtfLjfLTCvbmYimmH3WxpIiaSZyaBJyIbIBVHUz4nM'
    }


REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',  # This is for development
    ),
    'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}
#When set to False something else has to be updated as I can get any images in prod
CORS_ORIGIN_ALLOW_ALL = True 

CORS_ALLOWED_ORIGINS = [
	"http://localhost:80",
	"http://127.0.0.1:80",
	"http://localhost:8081",
	"http://127.0.0.1:8081",
]

# ----------------- OAUTH 2.0 - 42 INTRA SETTINGS -----------------:
# 42 Intra auth URL
API_42_AUTH_URL = 'https://api.intra.42.fr/oauth/authorize'
# 42 Intra access token endpoint
API_42_ACCESS_TOKEN_ENDPOINT = 'https://api.intra.42.fr/oauth/token'
# 42 Intra redirect URI
API_42_REDIRECT_URI = f'http://localhost:8000/42-callback/'
API_42_REDIRECT_URI_MATCH = f'http://localhost:8000/42-callback-match/'
# 42 Intra entrypoint URL
API_42_INTRA_ENTRYPOINT_URL = 'https://api.intra.42.fr/v2/me'
# 42 Intra frontend callback URL
API_42_FRONTEND_CALLBACK_URL = f'${FRONTEND_URL}/auth-success'
# one-time code lifetime in seconds
EXCHANGE_CODE_TIMEOUT = 30
# API CLIENT ID
INTRA_UID_42 = os.environ['CLIENT_ID']
# API CLIENT SECRET
INTRA_SECRET_42 = os.environ['CLIENT_SECRET']

API_GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
API_GOOGLE_REDIRECT_URI = 'http://localhost:8000/google-callback/'
GOOGLE_OAUTH_CLIENT_ID=os.environ['GOOGLE_OAUTH_CLIENT_ID']
GOOGLE_OAUTH_CLIENT_SECRET=os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
