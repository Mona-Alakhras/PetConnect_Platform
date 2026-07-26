"""
Django settings for petconnect project.
"""
 
from pathlib import Path
from decouple import config
 
BASE_DIR = Path(__file__).resolve().parent.parent
 
 
# ==========================================
# Core
# ==========================================
 
SECRET_KEY = config('SECRET_KEY')
 
DEBUG = config('DEBUG', default=False, cast=bool)
 
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)
 
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)
 
 
# ==========================================
# Applications
# ==========================================
 
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'petcare',
]
 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Serves collected static files in production without a separate web server.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
 
ROOT_URLCONF = 'petconnect.urls'
 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
 
WSGI_APPLICATION = 'petconnect.wsgi.application'
 
 
# ==========================================
# Database
# USE_MYSQL=True  -> MySQL (محلياً)
# USE_MYSQL=False -> SQLite (على PythonAnywhere)
# ==========================================
 
if config('USE_MYSQL', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='petconnect_db'),
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default='root'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='3306'),
            'OPTIONS': {'charset': 'utf8mb4'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
 
 
# ==========================================
# Authentication
# ==========================================
 
AUTH_USER_MODEL = 'petcare.User'
 
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
 
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'
 
# Password reset links stay valid for 3 days.
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24 * 3
 
 
# ==========================================
# Internationalization
# ==========================================
 
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Hebron'
USE_I18N = True
USE_TZ = True
 
 
# ==========================================
# Static & Media
# ==========================================
 
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
 
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        # Default works everywhere without a build step. In production set
        #   STATICFILES_BACKEND=whitenoise.storage.CompressedManifestStaticFilesStorage
        # and run `collectstatic` to get hashed, permanently cacheable filenames.
        'BACKEND': config(
            'STATICFILES_BACKEND',
            default='django.contrib.staticfiles.storage.StaticFilesStorage',
        ),
    },
}
# ما في داعي لـ STATICFILES_DIRS
# لأن مجلد static موجود جوّه تطبيق petcare و Django بلاقيه تلقائياً
 
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
 
# Upload limits — the app also validates per-image size in petcare/forms.py.
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024   # 20 MB per request
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024    # 5 MB before spilling to disk
DATA_UPLOAD_MAX_NUMBER_FILES = 10
 
 
# ==========================================
# Sessions & messages
# ==========================================
 
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # two weeks
CSRF_COOKIE_SAMESITE = 'Lax'
 
 
# ==========================================
# Email
# ==========================================
 
# Without SMTP credentials configured, mail is printed to the console instead
# of silently failing — handy in development.
if config('EMAIL_HOST_USER', default=''):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
 
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
 
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default=EMAIL_HOST_USER or 'no-reply@petconnect.local',
)
 
 
# ==========================================
# Logging
# ==========================================
 
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'petcare': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}
 
 
# ==========================================
# Production security (تشتغل فقط لما DEBUG=False)
# ==========================================
 
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 days
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
 