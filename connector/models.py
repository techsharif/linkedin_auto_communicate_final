from django.db import models

from app.models import LinkedInUser, BotTaskStatus
from messenger.models import CommonContactField, TimeStampedModel, \
    CampaignStepField, ContactStatus, Inbox, MessageField, Campaign
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
    location = models.CharField(max_length=254, blank=True, null=True)
    industry = models.CharField(max_length=254, blank=True, null=True)
    company = models.CharField(max_length=254, blank=True, null=True)
    title = models.CharField(max_length=254, blank=True, null=True)

    resultcount = models.IntegerField(blank=True, null=True)
    searchdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'connector_search'
        managed = True
        verbose_name = 'Search'
        verbose_name_plural = 'Searchs'

    def __str__(self):
        return self.search_name

    def result_status(self):
        return False if self.resultcount == None else True

    def result_count(self):
        return 0 if self.resultcount == None else self.resultcount
        

class SearchResult(CommonContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='searchresults',
                                on_delete=models.CASCADE, default=1)
    search = models.ForeignKey(Search, related_name='results',
                               on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200)
    connect_campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=ContactStatus.search_result_statuses, 
                              default=ContactStatus.CONNECT_REQ_N)
    

    class Meta:
        db_table = 'connector_searchresult'
        managed = True
        verbose_name = 'SearchResult'
        verbose_name_plural = 'SearchResults'

    def __str__(self):
        return self.name

    def search_result_status(self):
        if self.status == ContactStatus.IN_QUEUE_N:
            return 1
        else:
            return 0


# this is not used now, may be remvoed later
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
    
# this is not used now, may be remvoed later    
class ConnectorStep(TimeStampedModel, CampaignStepField):
    campaign = models.ForeignKey(ConnectorCampaign, related_name='campaignsteps',
                                 on_delete=models.CASCADE)
    
# this is not used now, may be remvoed later    
class ConnectMessage(MessageField):
    
    requestee = models.ForeignKey(Inbox, related_name='requestees',
                               on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=50, blank=True, 
                            choices=ContactStatus.MESSSAGETYPES,
                            default=ContactStatus.TALKING)
    connector = models.ForeignKey(ConnectorCampaign, related_name='connector_messages',
                                  on_delete=models.CASCADE, blank=True,
                                  null=True)
    is_connected = models.BooleanField(default=False)
    is_replied_other = models.BooleanField(default=False)
    
    class Meta():
        abstract = False
        
class TaskQueue(models.Model):
    owner = models.ForeignKey(LinkedInUser, related_name='taskqueues',
                                on_delete=models.CASCADE, default=1)
    status = models.CharField(max_length=20, choices=BotTaskStatus.statuses,
                              default=BotTaskStatus.QUEUED)
    queue_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('queue_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
