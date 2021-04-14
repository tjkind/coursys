from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coredata', '0024_longer_userid'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoffering',
            name='discussion_version',
            field=models.CharField(choices=[('OLD', 'Older Version'), ('NEW', 'Newest Version')], default='OLD', max_length=3),
        ),
    ]