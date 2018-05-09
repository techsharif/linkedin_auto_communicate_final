from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MemberShipField(models.Model):
    max_seat = models.IntegerField(default=1)
    max_search = models.IntegerField(default=5)
    max_search_result = models.IntegerField(default=500)
    price = models.FloatField(default=0.00)
    max_campaign = models.IntegerField(default=5)
    twoway_comm = models.BooleanField(default=True)
    welcome_message = models.BooleanField(default=True)
    custom_connect_message = models.BooleanField(default=False)
    company_title_search = models.BooleanField(default=False)
    withdrawn_invite = models.BooleanField(default=False)
    export_csv = models.BooleanField(default=False)    
    day_to_live = models.IntegerField(default=7)
    
    class Meta:
        abstract = True
        
class Profile(MemberShipField):
    user = models.OneToOneField(User, related_name='profile', 
                             on_delete=models.CASCADE)
        

class LinkedInUser(models.Model):
    profile = models.ForeignKey(Profile, related_name='linkedusers',
                                on_delete=models.CASCADE)
    email = models.CharField(max_length=254)
    password = models.CharField(max_length=32)
    latest_login = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.email
    
class UserServer(models.Model):
    owner = models.ForeignKey(LinkedInUser, related_name='servers',
                                      on_delete=models.CASCADE)
    ip = models.CharField(max_length=15, blank=True, null=True)
    active = models.BooleanField(default=True)
    
class Schedule(models.Model):
    owner = models.ForeignKey(LinkedInUser, related_name='schedules',
                                      on_delete=models.CASCADE)
    tz = models.CharField(max_length=50, default='America/New_York')
    start_from = models.IntegerField(default=0)
    start_to = models.IntegerField(default=12)
    is_weekendwork = models.BooleanField(default=True)

class MembershipType(MemberShipField):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    
    def __str__(self):
        return self.name
    
class Membership(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions', 
                             on_delete=models.CASCADE)
    membership_type = models.ManyToManyField(MembershipType)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.membership_type
    
    
class BotTaskStatus:
    QUEUED = 'Queued'
    RUNNING = 'Running'
    ERROR = 'Error'
    DONE = 'Done'
    statuses = (
        (QUEUED, QUEUED),
        (RUNNING, RUNNING),
        (ERROR, ERROR),
        (DONE, DONE),
    )
class BotTask(models.Model):
    
    owner = models.ForeignKey(LinkedInUser, related_name='bottasks',
                                      on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=BotTaskStatus.statuses, 
                              default=BotTaskStatus.QUEUED)
    lastrun_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
        
