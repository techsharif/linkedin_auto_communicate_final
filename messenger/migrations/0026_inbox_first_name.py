# Generated by Django 2.0.5 on 2018-06-07 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0025_inbox_countrycode'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]