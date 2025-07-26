from django.conf import settings
from django.utils.module_loading import import_string
from datetime import datetime

# Instantiate storage once, from your Django DEFAULT_FILE_STORAGE setting
StorageClass = import_string(settings.DEFAULT_FILE_STORAGE)
storage = StorageClass()

def user_receipt_upload_path(instance, filename):
    """
    Returns a path like:
    receipts/<user_id>/<YYYY-MM-DD>/receipt_<timestamp>.jpg
    """
    date = instance.date
    user_id = instance.user.id

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    new_filename = f"receipt_{timestamp}.jpg"

    date_path = date.strftime("%Y-%m-%d")

    return f"receipts/{user_id}/{date_path}/{new_filename}"
