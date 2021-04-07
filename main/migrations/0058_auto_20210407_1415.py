# Generated by Django 3.1.7 on 2021-04-07 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_requestqueue_is_recheck'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='handledxml',
            name='request',
        ),
        migrations.RemoveField(
            model_name='requestqueue',
            name='request_text',
        ),
        migrations.AddField(
            model_name='handledxml',
            name='request_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='requestqueue',
            name='request_id',
            field=models.IntegerField(default=0),
        ),
    ]
