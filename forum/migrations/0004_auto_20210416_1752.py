# Generated by Django 2.2.15 on 2021-04-16 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20210415_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumthread',
            name='status',
            field=models.CharField(choices=[('OPN', 'Open'), ('CLO', 'Closed'), ('HID', 'Hidden')], default='OPN', help_text='The thread status: Closed: no replies allowed, Hidden: cannot be seen', max_length=3),
        ),
    ]
