# Generated by Django 2.0.13 on 2019-03-01 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coredata', '0021_new_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.CharField(choices=[('ADVS', 'Advisor'), ('ADVM', 'Advisor Manager'), ('FAC', 'Faculty Member'), ('SESS', 'Sessional Instructor'), ('COOP', 'Co-op Staff'), ('INST', 'Other Instructor'), ('SUPV', 'Additional Supervisor'), ('DISC', 'Discipline Case Administrator'), ('DICC', 'Discipline Case Filer (email CC)'), ('ADMN', 'Departmental Administrator'), ('TAAD', 'TA Administrator'), ('TADM', 'Teaching Administrator'), ('GRAD', 'Grad Student Administrator'), ('GRPD', 'Graduate Program Director'), ('FUND', 'Grad Funding Administrator'), ('FDCC', 'Grad Funding Reminder CC'), ('TECH', 'Tech Staff'), ('GPA', 'GPA conversion system admin'), ('OUTR', 'Outreach Administrator'), ('INV', 'Inventory Administrator'), ('FACR', 'Faculty Viewer'), ('REPV', 'Report Viewer'), ('FACA', 'Faculty Administrator'), ('RELA', 'Relationship Database User'), ('SPAC', 'Space Administrator'), ('FORM', 'Form Administrator'), ('SYSA', 'System Administrator'), ('NONE', 'none')], max_length=4),
        ),
        migrations.AlterField(
            model_name='roleaccount',
            name='type',
            field=models.CharField(blank=True, choices=[('ADVS', 'Advisor'), ('ADVM', 'Advisor Manager'), ('FAC', 'Faculty Member'), ('SESS', 'Sessional Instructor'), ('COOP', 'Co-op Staff'), ('INST', 'Other Instructor'), ('SUPV', 'Additional Supervisor'), ('DISC', 'Discipline Case Administrator'), ('DICC', 'Discipline Case Filer (email CC)'), ('ADMN', 'Departmental Administrator'), ('TAAD', 'TA Administrator'), ('TADM', 'Teaching Administrator'), ('GRAD', 'Grad Student Administrator'), ('GRPD', 'Graduate Program Director'), ('FUND', 'Grad Funding Administrator'), ('FDCC', 'Grad Funding Reminder CC'), ('TECH', 'Tech Staff'), ('GPA', 'GPA conversion system admin'), ('OUTR', 'Outreach Administrator'), ('INV', 'Inventory Administrator'), ('FACR', 'Faculty Viewer'), ('REPV', 'Report Viewer'), ('FACA', 'Faculty Administrator'), ('RELA', 'Relationship Database User'), ('SPAC', 'Space Administrator'), ('FORM', 'Form Administrator'), ('SYSA', 'System Administrator'), ('NONE', 'none')], max_length=4, null=True),
        ),
    ]