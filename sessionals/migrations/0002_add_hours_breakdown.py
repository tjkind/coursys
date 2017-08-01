# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-13 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessionals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionalconfig',
            name='course_hours_breakdown',
            field=models.CharField(blank=True, help_text=b'e.g. 1x2HR Lecture, etc.  This will show up in the form in the column after the course department and number.', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='sessionalcontract',
            name='course_hours_breakdown',
            field=models.CharField(blank=True, help_text=b'e.g. 1x2HR Lecture, etc.  This will show up in the form in the column after the course department and number.', max_length=100, null=True),
        ),
    ]