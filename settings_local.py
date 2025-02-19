# Local settings that change on a per application / per environment basis
import os
from typing import List

PGSQLAPI_PASSWORD = os.getenv('PGSQLAPI_PASSWORD', 'pw')
PGSQLAPI_USER = os.getenv('PGSQLAPI_USER', 'postgres')
PGSQLAPI_HOST = os.getenv('PGSQLAPI_HOST', 'pgsqlapi')
POD_NAME = os.getenv('POD_NAME', 'pod')
PORTAL_NAME = os.getenv('PORTAL_NAME', 'saas')
ORGANIZATION_URL = os.getenv('ORGANIZATION_URL', 'example.com')

FINANCIAL_UI_URL = f'https://{PORTAL_NAME}.{ORGANIZATION_URL}/financial/'

ORG = ORGANIZATION_URL.split('.')[0]
APPLICATION_NAME = os.getenv('APPLICATION_NAME', f'{POD_NAME}_{ORG}_financial')

EMAIL_SUBJECT_PREFIX = f'[{ORG} Financial API]'
# These addresses should be Bcc'd in each notification email. Log in to this email to check any sent notifications
BCC_INVOICE_EMAILS: List = [
    os.getenv('BCC_INVOICE_EMAILS', None),
]

ALLOWED_HOSTS = (
    f'financial.{POD_NAME}.{ORGANIZATION_URL}',
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'financial': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'financial',
        'USER': PGSQLAPI_USER,
        'PASSWORD': PGSQLAPI_PASSWORD,
        'HOST': PGSQLAPI_HOST,
        'PORT': '5432',
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_default',
        'USER': PGSQLAPI_USER,
        'PASSWORD': PGSQLAPI_PASSWORD,
        'HOST': PGSQLAPI_HOST,
        'PORT': '5432',
    },
}

DATABASE_ROUTERS = [
    'financial.db_router.FinancialRouter',
]

INSTALLED_APPS = [
    'financial',
]

# Localisation
USE_I18N = False
USE_L10N = False

CLOUDCIX_INFLUX_TAGS = {
    'service_name': APPLICATION_NAME,
}
