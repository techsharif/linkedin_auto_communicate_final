from django.db import models


class User(models.Model):
    email = models.CharField(max_length=254)
    password = models.CharField(max_length=32)
    latest_login = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=1)

    class Meta:
        db_table = 'app_user'
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Profile(models.Model):
    account_id = models.IntegerField()
    enable_proxy = models.BooleanField(default=0)
    proxy_address = models.CharField(max_length=60, blank=True, null=True)
    proxy_authentication_type = models.CharField(max_length=254)
    proxy_username = models.CharField(max_length=254, blank=True, null=True)
    proxy_password = models.CharField(max_length=254, blank=True, null=True)
    license_type = models.CharField(max_length=254)

    def __str__(self):
        return self.account_id


    
        
