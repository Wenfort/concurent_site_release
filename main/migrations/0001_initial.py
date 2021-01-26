# Generated by Django 3.1.4 on 2021-01-19 20:14

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
                ('status', models.CharField(default='pending', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='HandledXml',
            fields=[
                ('request', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('xml', models.TextField()),
                ('status', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Payload',
            fields=[
                ('key', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('balance', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request', models.CharField(max_length=100)),
                ('site_age_concurency', models.IntegerField(default=0)),
                ('site_stem_concurency', models.IntegerField(default=0)),
                ('site_volume_concurency', models.IntegerField(default=0)),
                ('site_backlinks_concurency', models.IntegerField(default=0)),
                ('site_total_concurency', models.FloatField(default=0)),
                ('direct_upscale', models.FloatField(default=0)),
                ('status', models.CharField(default='progress', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RequestQueue',
            fields=[
                ('request', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserStatement',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('balance', models.IntegerField(default=0)),
                ('ordered_requests', models.TextField()),
            ],
        ),
    ]
