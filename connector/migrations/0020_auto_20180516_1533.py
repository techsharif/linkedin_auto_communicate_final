# Generated by Django 2.0.5 on 2018-05-16 15:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20180515_0653'),
        ('connector', '0019_auto_20180516_0428'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskqueue',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taskqueue',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='taskqueues', to='app.LinkedInUser'),
        ),
        migrations.AddField(
            model_name='taskqueue',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

