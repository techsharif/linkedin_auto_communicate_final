# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-27 17:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('searchname', models.CharField(max_length=254)),
                ('keyword', models.CharField(max_length=254)),
                ('resultcount', models.CharField(max_length=10)),
                ('searchdate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='SearchResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('company', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('searchid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='connector.Search')),
            ],
            options={
                'verbose_name': 'SearchResult',
                'verbose_name_plural': 'SearchResults',
            },
        ),
    ]
