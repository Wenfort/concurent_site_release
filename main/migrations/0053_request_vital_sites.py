# Generated by Django 3.1.7 on 2021-03-19 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_auto_20210309_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='vital_sites',
            field=models.CharField(default='', max_length=100),
        ),
    ]
