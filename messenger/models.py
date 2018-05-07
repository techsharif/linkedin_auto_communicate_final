from django.db import models

from app.models import LinkedInUser


try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ContactStatus(object):
    
    ALL = 'All'
    LATER = 'Later'
    MESSAGE = 'Message'
    NO_INTEREST = 'No Interest'
    OLD_CONNECT = 'Old Connect'
    REPLIED = 'Replied'
    TALKING = 'Talking'
    TALKING_REPLIED = 'Talking & Replied'
    
    CONNECTED = 'Connected'
    CONNECT_REQUESTED = 'Connect Requested'
    DISCONNECTED = 'Disconnected'
    IN_QUEUE = 'In Queue'
    
    WELCOME_MES = 'Welcome Mes'
    
    contact_statues = (
        (ALL, ALL),
        (LATER, LATER),
        (NO_INTEREST, NO_INTEREST),
        (OLD_CONNECT, OLD_CONNECT),
        (REPLIED, REPLIED),
        (TALKING, TALKING),
        (TALKING_REPLIED, TALKING_REPLIED),
        )
    
    IMPORTED = 'Imported'
    CONNECTOR = 'connector'
    MESSENGER = 'messenger'
    
    connector_messengers = (
        (IMPORTED, IMPORTED),
        (IN_QUEUE, IN_QUEUE),
        
        )
    
    inbox_statuses = (
        (ALL, ALL),
        (LATER, LATER),
        (NO_INTEREST, NO_INTEREST),
        (OLD_CONNECT, OLD_CONNECT),
        (REPLIED, REPLIED),
        (TALKING, TALKING),
        (TALKING_REPLIED, TALKING_REPLIED),
        (CONNECTED, CONNECTED),
        (OLD_CONNECT, OLD_CONNECT),
        (DISCONNECTED, DISCONNECTED),
        (IN_QUEUE, IN_QUEUE),
        (WELCOME_MES, WELCOME_MES),
        )

class CommonContactField(models.Model):
    company = models.CharField(max_length=100, db_index=True, blank=True, 
                               null=True)
    industry = models.CharField(max_length=100, db_index=True, blank=True, 
                                null=True)
    location = models.CharField(max_length=100, db_index=True, blank=True, 
                                null=True)
    title = models.CharField(max_length=100, db_index=True, blank=True, 
                                null=True)
    
    class Meta:
        abstract = True
    
class ContactField(CommonContactField):
    
    name = models.CharField(max_length=100, db_index=True)
    
    latest_acitvity = models.DateTimeField()
    
    class Meta:
        abstract = True

class Contact(TimeStampedModel, ContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='contacts',
                                on_delete=models.CASCADE)
    # source of this contact
    connector_messenger = models.CharField(max_length=20, 
                                           choices=ContactStatus.connector_messengers,
                                           default=ContactStatus.IMPORTED)
    status = models.CharField(max_length=20, 
                              choices=ContactStatus.contact_statues, 
                              default=ContactStatus.OLD_CONNECT)
    notes = models.TextField()

    def __str__(self):
        return force_text(str(self.account_id) + "  " + self.name)

    class Meta():
        abstract = False
        # db_table = 'contacts'

class Campaign(TimeStampedModel):
    owner = models.ForeignKey(LinkedInUser, related_name='messegercampaigns',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=100, db_index=True)
    status = models.BooleanField(default=True)
    contacts = models.ManyToManyField(Contact)
    copy_campaign = models.ForeignKey('self', on_delete=models.SET_NULL,
                                       blank=True, null=True)
    
    def __str__(self):
        return force_text(str(self.account_id) + "  " + self.title)

class CampaignStepField(models.Model):
    step_number = models.IntegerField(db_index=True, default=1)
    message = models.TextField()
    action = models.CharField(max_length=100, db_index=True)
    class Meta:
        abstract = False
        

class CampaignStep(TimeStampedModel, CampaignStepField):
    campaign = models.ForeignKey(Campaign, related_name='campaignsteps',
                                 on_delete=models.CASCADE)
    
    

    class Meta():
        abstract = False
        # db_table = 'campaign_setps'


class Message(TimeStampedModel):
    owner = models.ForeignKey(LinkedInUser, related_name='senders',
                              on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, related_name='receivers',
                               on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    time = models.DateTimeField()

    class Meta():
        abstract = False
        
class Inbox(ContactField):
    owner = models.ForeignKey(LinkedInUser, related_name='inboxes',
                                on_delete=models.CASCADE)
    status = models.CharField(max_length=20, 
                              choices=ContactStatus.inbox_statuses, 
                              default=ContactStatus.OLD_CONNECT)
