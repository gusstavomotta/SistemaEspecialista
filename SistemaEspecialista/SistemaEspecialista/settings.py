from pathlib import Path
import os
from decouple import config

# ========================
# BASE DIR
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent


# ========================
# SEGURANÇA
# ========================
SECRET_KEY = 'django-insecure-9=i)nuz3j6cyo=-u!xj_$rdq9s#vvxn6vpevw-9qikmv3za8zl'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# ========================
# APLICAÇÕES INSTALADAS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'EscalaPoms',
]


# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

]


# ========================
# URL & WSGI
# ========================
ROOT_URLCONF = 'SistemaEspecialista.urls'
WSGI_APPLICATION = 'SistemaEspecialista.wsgi.application'


# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Templates personalizados
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ========================
# BANCO DE DADOS
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'teste',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# ========================
# AUTENTICAÇÃO
# ========================
AUTHENTICATION_BACKENDS = [
    'EscalaPoms.backends.CPFBackend',  # Login via CPF
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'


# ========================
# VALIDAÇÃO DE SENHA
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# INTERNACIONALIZAÇÃO
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ========================
# ARQUIVOS ESTÁTICOS E MÍDIA
# ========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'EscalaPoms/static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ========================
# PADRÕES GERAIS
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FROM_EMAIL = 'sistemaespecialistaunisc@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_HOST = config('EMAIL_HOST')