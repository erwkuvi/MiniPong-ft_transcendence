# PROD
from .common import *
import os
import environ

env = environ.Env()
environ.Env.read_env()

# For https connection 
BASE_URL_SCHEME = 'https'

HOST_IP = env('HOST_IP')
FRONTEND_URL = env('FRONTEND_URL')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    os.getenv("NGINX_SERVER_NAME"),
    "localhost",
    "127.0.0.1",
    "django",
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# django-sendfile is a package that abstracts the X-Accel-Redirect (for Nginx) and similar mechanisms for other web servers


SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
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
         'rest_framework.permissions.IsAuthenticated',  # by default
    ),
    'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
    ),
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]


CORS_ORIGIN_ALLOW_ALL = False


CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "{FRONTEND_URL}"
	# "https://localhost",
]

# ----------------- OAUTH 2.0 - 42 INTRA SETTINGS -----------------:
# 42 Intra auth URL
API_42_AUTH_URL = 'https://api.intra.42.fr/oauth/authorize'
# 42 Intra access token endpoint
API_42_ACCESS_TOKEN_ENDPOINT = 'https://api.intra.42.fr/oauth/token'
# 42 Intra redirect URI
API_42_REDIRECT_URI = f'{FRONTEND_URL}/42-callback/'
API_42_REDIRECT_URI_MATCH = f'{FRONTEND_URL}/42-callback-match/'
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
API_GOOGLE_REDIRECT_URI = '{FRONTEND_URL}/google-callback/'
GOOGLE_OAUTH_CLIENT_ID=os.environ['GOOGLE_OAUTH_CLIENT_ID']
GOOGLE_OAUTH_CLIENT_SECRET=os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
