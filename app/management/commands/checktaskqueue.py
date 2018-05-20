import json

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import BotTask, BotTaskStatus, BotTaskType
from connector.models import TaskQueue, Search
from messenger.models import Campaign


class Command(BaseCommand):
    help = 'collect_search : it will process all pending search results'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.check_or_add_search_task()
        # self.check_taskqueue()

    def check_and_message_campaign(self):

        task_queues = TaskQueue.objects.filter(status=BotTaskStatus.QUEUED).all()
        for task in task_queues:
            BotTask.objects.create(name=task.content_object, task_type=task.queue_type,
                                   owner=task.owner, status=task.status, extra_id = task.queue_type_id)

    def check_or_add_search_task(self):
        pending_task_list = BotTask.objects.exclude(status__in=[BotTaskStatus.DONE, BotTaskStatus.ERROR], task_type=BotTaskType.SEARCH)
        for pending_task in pending_task_list:
            search = Search.objects.get(id=pending_task.search_id())
            queue_type = ContentType.objects.get_for_model(search)
            task_queue = TaskQueue.objects.filter(object_id=search.id, queue_type=queue_type)
            if task_queue:
                task = task_queue[0]
                pending_task.status = task.status
                pending_task.save()
            else:
                search = Search.objects.get(id=pending_task.extra_id)
                TaskQueue(content_object=search, owner=pending_task.owner).save()

    def check_or_add_connect_campaign_task(self):
        connect_campaigns = Campaign.objects.filter(status=True, is_bulk=False)
        for connect_campaign in connect_campaigns:
            queue_type = ContentType.objects.get_for_model(connect_campaign)
            task_queue = TaskQueue.objects.filter(object_id=connect_campaign.id, queue_type=queue_type)
            if task_queue:
                task = task_queue[0]
                bottask, created = BotTask(owner=connect_campaign.owner, task_type=BotTaskType.CHECKCONNECT,
                                           extra_id=connect_campaign.id, name=BotTaskType.CHECKCONNECT)
                if not created:
                    task.status = bottask.status
                    task.save()
            else:
                TaskQueue(owner=connect_campaign.owner, content_object=connect_campaign).save()
                bottask, created = BotTask(owner=connect_campaign.owner, task_type=BotTaskType.POSTCONNECT,
                        extra_id=connect_campaign.id, name=BotTaskType.POSTCONNECT)
                bottask.status = BotTaskStatus.QUEUED
                bottask.save()

    def check_or_add_message_campaign_task(self):
        connect_campaigns = Campaign.objects.filter(status=True, is_bulk=True)
        for connect_campaign in connect_campaigns:
            queue_type = ContentType.objects.get_for_model(connect_campaign)
            task_queue = TaskQueue.objects.filter(object_id=connect_campaign.id, queue_type=queue_type)
            if task_queue:
                task = task_queue[0]
                bottask, created = BotTask(owner=connect_campaign.owner, task_type=BotTaskType.CHECKMESSAGE,
                                           extra_id=connect_campaign.id, name=BotTaskType.CHECKMESSAGE)
                if not created:
                    task.status = bottask.status
                    task.save()
            else:
                TaskQueue(owner=connect_campaign.owner, content_object=connect_campaign).save()
                bottask, created = BotTask(owner=connect_campaign.owner, task_type=BotTaskType.POSTMESSAGE,
                        extra_id=connect_campaign.id, name=BotTaskType.POSTMESSAGE)
                bottask.status = BotTaskStatus.QUEUED
                bottask.save()