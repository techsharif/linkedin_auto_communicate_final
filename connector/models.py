from django.db import models

from app.models import LinkedInUser, BotTaskStatus
from messenger.models import CommonContactField, TimeStampedModel, \
    CampaignStepField, ContactStatus, Inbox, MessageField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Search(CommonContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='searches',
                                on_delete=models.CASCADE, default=1)
    search_name = models.CharField(max_length=254)
    # how to deal with either of these 3 is null in form
    keyword = models.CharField(max_length=254, blank=True, null=True)
    url_search = models.URLField(blank=True, null=True)
    sales_search = models.URLField(blank=True, null=True)
    
    resultcount = models.CharField(max_length=10)
    searchdate = models.DateTimeField()

    class Meta:
        db_table = 'connector_search'
        managed = True
        verbose_name = 'Search'
        verbose_name_plural = 'Searchs'

    def __str__(self):
        return self.search_name
        

class SearchResult(CommonContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='searchresults',
                                on_delete=models.CASCADE, default=1)
    search = models.ForeignKey(Search, related_name='results',
                               on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, 
                              choices=ContactStatus.search_result_statuses, 
                              default=ContactStatus.CONNECT_REQ)
    

    class Meta:
        db_table = 'connector_searchresult'
        managed = True
        verbose_name = 'SearchResult'
        verbose_name_plural = 'SearchResults'

    def __str__(self):
        return self.name


class ConnectorCampaign(models.Model):
    owner = models.ForeignKey(LinkedInUser, related_name='connectorcampaigns',
                                on_delete=models.CASCADE, default=1)
    connector_name = models.CharField(max_length=200)
     
    copy_connector = models.ForeignKey('self', on_delete=models.SET_NULL,
                                       blank=True, null=True)
    
    created_at = models.DateTimeField()
    status = models.BooleanField()
    connectors = models.ManyToManyField(Inbox)
    
    def __str__(self):
        return self.connector_name
    
    
class ConnectorStep(TimeStampedModel, CampaignStepField):
    campaign = models.ForeignKey(ConnectorCampaign, related_name='campaignsteps',
                                 on_delete=models.CASCADE)
    
class ConnectMessage(MessageField):
    
    requestee = models.ForeignKey(Inbox, related_name='requestees',
                               on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=50, blank=True, 
                            choices=ContactStatus.MESSSAGETYPES,
                            default=ContactStatus.TALKING)
    connector = models.ForeignKey(ConnectorCampaign, related_name='connector_messages',
                                  on_delete=models.CASCADE, blank=True,
                                  null=True)
    class Meta():
        abstract = False
        
class TaskQueue(models.Model):
    status = models.CharField(max_length=10, choices=BotTaskStatus.statuses, 
                              default=BotTaskStatus.QUEUED)
    queue_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('queue_type', 'object_id')
    
    
