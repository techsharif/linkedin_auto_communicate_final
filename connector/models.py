from django.db import models

from app.models import LinkedInUser
from messenger.models import CommonContactField, TimeStampedModel, \
    CampaignStepField


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
        return self.searc_hname
        

class SearchResult(CommonContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='searchresults',
                                on_delete=models.CASCADE, default=1)
    search = models.ForeignKey(Search, related_name='results',
                               on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=200)
    # other fields are inherited from CommonContactField

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
    connectors = models.ManyToManyField(SearchResult)
    
    def __str__(self):
        return self.connector_name
    
    
class ConnectorStep(TimeStampedModel, CampaignStepField):
    campaign = models.ForeignKey(ConnectorCampaign, related_name='campaignsteps',
                                 on_delete=models.CASCADE)
    