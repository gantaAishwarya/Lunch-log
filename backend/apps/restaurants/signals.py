from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

@receiver(post_migrate)
def create_fetch_task(sender, **kwargs):
    if sender.name != "backend.apps.restaurants":
        return

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=24,
        period=IntervalSchedule.HOURS
    )

    task_name = "Fetch Berlin restaurants daily"
    task_path = "backend.apps.restaurants.tasks.fetch_restaurant_data_for_city"
    args = json.dumps(["Berlin"])

    if not PeriodicTask.objects.filter(name=task_name).exists():
        PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task=task_path,
            args=args,
        )
