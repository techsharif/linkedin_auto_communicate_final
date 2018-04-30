from django.db import models


class User(models.Model):
    email = models.CharField(max_length=254)
    password = models.CharField(max_length=32)

    class Meta:
        db_table = 'app_user'
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
