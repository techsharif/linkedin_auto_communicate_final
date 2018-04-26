from django.db import models
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Campaign(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    account_id = models.IntegerField(db_index=True)
    title = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=100, db_index=True)
    
    def __str__(self):
        return force_text(str(self.account_id) + "  " + self.title)

    class Meta():
        abstract = False
        # db_table = 'campaigns'


class Contact(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    account_id = models.IntegerField(db_index=True)
    campaign_id = models.IntegerField(db_index=True, blank=True, null=True)
    status = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    company = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    industry = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    location = models.CharField(max_length=100, db_index=True, blank=True, null=True)
    latest_acitvity = models.DateTimeField()
    
    def __str__(self):
        return force_text(str(self.account_id) + "  " + self.name)

    class Meta():
        abstract = False
        # db_table = 'contacts'



class CampaignSetp(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    campaign_id = models.IntegerField(db_index=True, blank=True, null=True)
    setp_number = models.IntegerField(db_index=True, default=1)
    message = models.TextField()
    action = models.CharField(max_length=100, db_index=True)
    

    class Meta():
        abstract = False
        # db_table = 'campaign_setps'
