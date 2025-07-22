from django.conf import settings
from django.utils.module_loading import import_string
from datetime import datetime

# Instantiate storage once, from your Django DEFAULT_FILE_STORAGE setting
StorageClass = import_string(settings.DEFAULT_FILE_STORAGE)
storage = StorageClass()

def user_receipt_upload_path(instance, filename):
    """
    Returns a path like:
    user_<user_id>/YYYY-MM/DD/receipt_YYYYMMDDTHHMMSS_<uuid>.<ext>
    Supports filtering by month and specific day.
    """
    date = instance.date
    user_id = instance.user.id

    # Extract file extension safely (default to jpg if missing)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")

    new_filename = f"receipt_{timestamp}.{ext}"

    # Generate path: user_12/2025-07/21/
    month_path = date.strftime("%Y-%m")
    day_path = date.strftime("%d")

    return f"user_{user_id}/{month_path}/{day_path}/{new_filename}"
