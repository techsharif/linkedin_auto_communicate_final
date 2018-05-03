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
