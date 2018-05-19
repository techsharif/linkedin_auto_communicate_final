from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import BotTask, BotTaskStatus, BotTaskType
from connector.models import TaskQueue


class Command(BaseCommand):
    help = 'collect_search : it will process all pending search results'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        task_queues = TaskQueue.objects.filter(status=BotTaskStatus.QUEUED).all()
        for task in task_queues:
            BotTask.objects.create(name=task.content_object, task_type=task.queue_type,
                                   owner=task.owner, status=task.status, extra_info={'id':task.queue_type_id})
