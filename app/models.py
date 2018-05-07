from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LinkedInUser(models.Model):
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

class MembershipType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    max_seat = models.IntegerField(default=1)
    max_search = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name
    
class Membership(models.Model):
    user = models.ForeignKey(User, related_name='profiles', 
                             on_delete=models.CASCADE)
    membership_type = models.ManyToManyField(MembershipType)
    valid_from = models.DateTimeField(blank=True, null=True)
    valid_to = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

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
    
        
