# Generated by Django 3.1.5 on 2021-02-10 07:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20210210_0659'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requestqueue',
            old_name='request',
            new_name='request_text',
        ),
    ]
