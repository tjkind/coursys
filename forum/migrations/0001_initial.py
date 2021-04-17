# Generated by Django 2.2.15 on 2021-04-13 23:11

import autoslug.fields
import courselib.json_fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('coredata', '0025_add_discuss_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumThread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='A brief description of the thread', max_length=140)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity_at', models.DateTimeField(auto_now_add=True)),
                ('reply_count', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('OPN', 'Open'), ('ANS', 'Answered'), ('CLO', 'Closed'), ('HID', 'Hidden')], default='OPN', help_text='The thread status: Closed: no replies allowed, Hidden: cannot be seen', max_length=3)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique_with=['offering'])),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Member')),
                ('offering', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.CourseOffering')),
            ],
        ),
        migrations.CreateModel(
            name='ForumReply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('VIS', 'Visible'), ('HID', 'Hidden')], default='VIS', max_length=3)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='autoslug', unique_with=['thread'])),
                ('config', courselib.json_fields.JSONField(default=dict)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='coredata.Member')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='forum.ForumReply')),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.ForumThread')),
            ],
        ),
    ]