import os
from pathlib import Path

from .env import env

BASE_DIR = Path(__file__).resolve().parent.parent

env.read_env(os.path.join(BASE_DIR.parent, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_q",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "notifications",
    "storages",
]

INSTALLED_EXTENSIONS = [
    "users",
    "league",
    "match",
    "bet",
    "event",
    "deployment",
]

# if DEBUG:
#     INSTALLED_APPS.append('debug_toolbar')
#     INSTALLED_APPS.append('silk')
#

INSTALLED_APPS += INSTALLED_EXTENSIONS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# if DEBUG:
#     MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
#     MIDDLEWARE.append("silk.middleware.SilkyMiddleware")

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "base.wsgi.application"

if env("ENVIRONMENT") == "ci":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

if env("USE_S3"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3.S3Storage"
    STATICFILES_STORAGE = "storages.backends.s3.S3Storage"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "bet-home"
LOGIN_URL = "login"

API_TOKEN = env("API_TOKEN")

Q_CLUSTER = {
    "name": "DjangORM",
    "workers": 1,
    "timeout": 60,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

INTERNAL_IPS = [
    "127.0.0.1",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}

SILKY_PYTHON_PROFILER = True


if env("ENVIRONMENT") == "prod":
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
