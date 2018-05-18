# Generated by Django 2.0.5 on 2018-05-18 09:12

from django.db import migrations

def send_linkedin_id(apps, schema_editor):
    searchresult = apps.get_model('connector', 'searchresult')
    for row in searchresult.objects.all():
        row.linkedin_id = row.id
        row.save(update_fields=['linkedin_id'])

class Migration(migrations.Migration):

    dependencies = [
        ('connector', '0026_auto_20180518_1545'),
    ]

    operations = [
        migrations.RunPython(send_linkedin_id)
    ]
