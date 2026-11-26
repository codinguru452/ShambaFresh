
"""
Settings for ShambaFresh Agrovet.

Local development:
    SQLite

Production:
    TiDB Cloud using Django's MySQL backend and PyMySQL.
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# --------------------------------------------------
# BASE CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DEBUG", "True").strip().lower() == "true"

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "local-development-only-change-me"
)

if not DEBUG and SECRET_KEY == "local-development-only-change-me":
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY in production."
    )

# --------------------------------------------------
# ALLOWED HOSTS
# --------------------------------------------------

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]

RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

# --------------------------------------------------
# INSTALLED APPS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "myapp",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --------------------------------------------------
# URL AND TEMPLATE CONFIGURATION
# --------------------------------------------------

ROOT_URLCONF = "mpesaapi.urls"

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

WSGI_APPLICATION = "mpesaapi.wsgi.application"

# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------
# Local: SQLite
# Production: TiDB Cloud

TIDB_HOST = os.getenv("TIDB_HOST", "").strip()

if TIDB_HOST:

    TIDB_CA_PATH = os.getenv("TIDB_CA_PATH", "").strip()

    if not TIDB_CA_PATH:
        raise ImproperlyConfigured(
            "TIDB_CA_PATH must point to the TiDB CA certificate."
        )

    if not os.path.isfile(TIDB_CA_PATH):
        raise ImproperlyConfigured(
            f"TiDB CA certificate not found: {TIDB_CA_PATH}"
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("TIDB_DB_NAME", "shambafresh"),
            "USER": os.getenv("TIDB_USER", ""),
            "PASSWORD": os.getenv("TIDB_PASSWORD", ""),
            "HOST": TIDB_HOST,
            "PORT": os.getenv("TIDB_PORT", "4000"),
            "CONN_MAX_AGE": 60,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {
                "ssl": {
                    "ca": TIDB_CA_PATH,
                    "check_hostname": True,
                },
            },
        }
    }

else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# --------------------------------------------------
# LANGUAGE AND TIME ZONE
# --------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = False

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# RENDER HTTPS CONFIGURATION
# --------------------------------------------------

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https"
)

if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"

# --------------------------------------------------
# MPESA DARAJA CONFIGURATION
# --------------------------------------------------

MPESA_CONSUMER_KEY = os.getenv(
    "MPESA_CONSUMER_KEY", ""
).strip()

MPESA_CONSUMER_SECRET = os.getenv(
    "MPESA_CONSUMER_SECRET", ""
).strip()

MPESA_SHORTCODE = os.getenv(
    "MPESA_SHORTCODE", "174379"
).strip()

MPESA_PASSKEY = os.getenv(
    "MPESA_PASSKEY", ""
).strip()

MPESA_CALLBACK_URL = os.getenv(
    "MPESA_CALLBACK_URL", ""
).strip()

MPESA_BASE_URL = os.getenv(
    "MPESA_BASE_URL",
    "https://sandbox.safaricom.co.ke"
).strip().rstrip("/")

MPESA_TRANSACTION_TYPE = os.getenv(
    "MPESA_TRANSACTION_TYPE",
    "CustomerPayBillOnline"
).strip()
