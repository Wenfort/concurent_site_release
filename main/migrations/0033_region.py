# Generated by Django 3.1.5 on 2021-02-17 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_ticket_user_ticket_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('region_id', models.IntegerField(default=0)),
            ],
        ),
    ]