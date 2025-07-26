from .base import *

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# ------------------------------------------------------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
# NEVER use this key in production
# ------------------------------------------------------------------------------
SECRET_KEY = env.str(
    "SECRET_KEY",
    default="django-insecure-r6l0y)!pv)0_2_l_x3=v7c7)0txa==ke3y0&x3_lh!%kjrkndq"
)

# ------------------------------------------------------------------------------
# Debug mode (turn OFF in production!)
# ------------------------------------------------------------------------------
DEBUG = True

# ------------------------------------------------------------------------------
# Local Minio setup
# ------------------------------------------------------------------------------

AWS_ACCESS_KEY_ID = env.str("MINIO_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = env.str("MINIO_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("MINIO_BUCKET")
AWS_S3_ENDPOINT_URL = env.str("MINIO_ENDPOINT")
AWS_S3_REGION_NAME = env.str("MINIO_REGION")
AWS_S3_ADDRESSING_STYLE = "path" 
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False 

AWS_QUERYSTRING_AUTH = False 


# ------------------------------------------------------------------------------
# Caching - local memory cache, suitable for development only
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "dev-cache",
    }
}

# TTL for cache: 2 hours
CACHE_TTL = 60 * 60 * 2

# ------------------------------------------------------------------------------
# Admin URL - easier to change if needed
# ------------------------------------------------------------------------------
ADMIN_URL = "admin/"