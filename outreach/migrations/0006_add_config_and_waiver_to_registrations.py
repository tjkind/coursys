# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-29 14:54
from __future__ import unicode_literals

import courselib.json_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outreach', '0005_add_registration_closed_option_to_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outreacheventregistration',
            name='waiver',
        ),
        migrations.AddField(
            model_name='outreachevent',
            name='config',
            field=courselib.json_fields.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='outreacheventregistration',
            name='config',
            field=courselib.json_fields.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='outreacheventregistration',
            name='participation_waiver',
            field=models.BooleanField(default=False, help_text=b'Check this box if you agree with the participation waiver.', verbose_name=b"I agree to HOLD HARMLESS AND INDEMNIFY the FAS Outreach Program and SFU for any and all liability to which the University has no legal obligation, including but not limited to, any damage to the property of, or personal injury to my child or for injury and/or property damage suffered by any third party resulting from my child's actions whilst participating in the program. By signing this consent, I agree to allow SFU staff to provide or cause to be provided such medical services as the University or medical personnel consider appropriate. The FAS Outreach Program reserves the right to refuse further participation to any participant for rule infractions."),
        ),
        migrations.AddField(
            model_name='outreacheventregistration',
            name='photo_waiver',
            field=models.BooleanField(default=False, help_text=b'Check this box if you agree with the photo waiver.', verbose_name=b'I, hereby authorize the Faculty of Applied Sciences Outreach program of Simon Fraser University to photograph, audio record, video record, podcast and/or webcast the Child (digitally or otherwise) without charge; and to allow the FAS Outreach Program to copy, modify and distribute in print and online, those images that include your child in whatever appropriate way either the FAS Outreach Program and/or SFU sees fit without having to seek further approval. No names will be used in association with any images or recordings.'),
        ),
    ]