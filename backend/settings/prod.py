from .base import *
import logging
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# ------------------------------------------------------------------------------
# General
# ------------------------------------------------------------------------------
DEBUG = False

SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY must be set in production.")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS settings
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=60)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)

# Prevent content type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = ["whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------------------------------------------------
# Caching
# ------------------------------------------------------------------------------
CACHE_TTL = 60 * 60 * 2  # 2 hours

# ------------------------------------------------------------------------------
# Admin
# ------------------------------------------------------------------------------
ADMIN_URL = env("DJANGO_ADMIN_URL", default="backoffice/")
ADMINS = [("metycle", "admin@metycle.net")]

# ------------------------------------------------------------------------------
# Email
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", default="hi@metycle.net")
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default="[metycle] ")


# ------------------------------------------------------------------------------
# AWS set up
# ------------------------------------------------------------------------------

AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_BUCKET")
AWS_S3_ENDPOINT_URL = env.str("AWS_ENDPOINT")
AWS_S3_REGION_NAME = env.str("AWS_REGION")
AWS_S3_ADDRESSING_STYLE = "path" 
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False 

AWS_QUERYSTRING_AUTH = False 


# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s %(process)d %(thread)d: %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}

# ------------------------------------------------------------------------------
# Sentry Integration
# ------------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.5,
        profiles_sample_rate=0.5,
        send_default_pii=True,
    )