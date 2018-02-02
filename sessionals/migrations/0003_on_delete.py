# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-18 17:09
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessionals', '0002_add_hours_breakdown'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionalaccount',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique=True),
        ),
        migrations.AlterField(
            model_name='sessionalaccount',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='sessionalconfig',
            name='course_hours_breakdown',
            field=models.CharField(blank=True, help_text='e.g. 1x2HR Lecture, etc.  This will show up in the form in the column after the course department and number.', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='sessionalconfig',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique=True),
        ),
        migrations.AlterField(
            model_name='sessionalconfig',
            name='unit',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sessionals.SessionalAccount'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='appt_guarantee',
            field=models.CharField(choices=[('GUAR', 'Appointment Guaranteed'), ('COND', 'Appointment Conditional Upon Enrolment')], default='GUAR', max_length=4, verbose_name='Appoinment Guarantee'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='appt_type',
            field=models.CharField(choices=[('INIT', 'Initial Appointment to this Position Number'), ('REAP', 'Reappointment to Same Position Number or Revision')], default='INIT', max_length=4, verbose_name='Appointment Type'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='contact_hours',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Weekly Contact Hours'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='course_hours_breakdown',
            field=models.CharField(blank=True, help_text='e.g. 1x2HR Lecture, etc.  This will show up in the form in the column after the course department and number.', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='offering',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.CourseOffering'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='sessional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.AnyPerson'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='sin',
            field=models.CharField(help_text='Social Insurance Number - 000000000 if unknown', max_length=30, verbose_name='SIN'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique=True),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Unit'),
        ),
        migrations.AlterField(
            model_name='sessionalcontract',
            name='visa_verified',
            field=models.BooleanField(default=False, help_text="I have verified this sessional's visa information"),
        ),
    ]