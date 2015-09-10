# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import courselib.conditional_save
import courselib.json_fields


class Migration(migrations.Migration):

    dependencies = [
        ('coredata', '0003_remove_computingaccount'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_name', models.CharField(max_length=32)),
                ('first_name', models.CharField(max_length=32)),
                ('middle_name', models.CharField(max_length=32, null=True, blank=True)),
                ('pref_first_name', models.CharField(max_length=32, null=True, blank=True)),
                ('title', models.CharField(max_length=4, null=True, blank=True)),
                ('config', courselib.json_fields.JSONField(default={})),
                ('userid', models.CharField(null=True, max_length=8, blank=True, help_text=b'SFU Unix userid (i.e. part of SFU email address before the "@").', unique=True, verbose_name=b'User ID', db_index=True)),
            ],
            options={
                'ordering': ['last_name', 'first_name', 'userid'],
                'abstract': False,
                'verbose_name_plural': 'People',
            },
            bases=(models.Model, courselib.conditional_save.ConditionalSaveMixin),
        ),
        migrations.CreateModel(
            name='TemporaryPerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_name', models.CharField(max_length=32)),
                ('first_name', models.CharField(max_length=32)),
                ('middle_name', models.CharField(max_length=32, null=True, blank=True)),
                ('pref_first_name', models.CharField(max_length=32, null=True, blank=True)),
                ('title', models.CharField(max_length=4, null=True, blank=True)),
                ('config', courselib.json_fields.JSONField(default={})),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, courselib.conditional_save.ConditionalSaveMixin),
        ),
    ]
