# Generated by Django 3.1.4 on 2020-12-29 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('age', models.IntegerField(default=0)),
                ('unique_backlinks', models.IntegerField(default=0)),
                ('total_backlinks', models.IntegerField(default=0)),
            ],
        ),
    ]
