# Custom configuration file

# Set Environment
ENVIRONMENT = 'PRODUCTION'
# ENVIRONMENT = 'DEVELOPMENT'

SECRET_KEY = 'SECRET_KEY=************************************'

if ENVIRONMENT == 'PRODUCTION':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mcs',
            'USER': 'mon',
            'PASSWORD': '*****',
            'HOST': 'localhost',
            'PORT': '',
        }
    }
elif ENVIRONMENT == 'DEVELOPMENT':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mcsdev',
            'USER': 'mon',
            'PASSWORD': '******',
            'HOST': 'localhost',
            'PORT': '',
        }
    }    

OIDC_RP_CLIENT_ID = 'mcs'
OIDC_RP_CLIENT_SECRET = '**********************'

OIDC_RP_CLIENT_ID = 'mcs'
OIDC_RP_CLIENT_SECRET = '******'


OIDC_BASE_URL = ""
OIDC_OP_TOKEN_ENDPOINT = ""
OIDC_OP_AUTHORIZATION_ENDPOINT = ""
OIDC_OP_JWKS_ENDPOINT = ""
OIDC_OP_USER_ENDPOINT = ""
OIDC_OP_LOGOUT_URL_METHOD = "authtest.auth.provider_logout"


SD_URL = ""
SD_LOGIN = "nagios"
SD_PWD = "*********"
