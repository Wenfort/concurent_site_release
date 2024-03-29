# Generated by Django 3.1.7 on 2021-05-25 10:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
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
                ('domain_group', models.IntegerField(default=0)),
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
            name='Region',
            fields=[
                ('id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=150)),
                ('age_concurency', models.IntegerField(default=0)),
                ('stem_concurency', models.IntegerField(default=0)),
                ('volume_concurency', models.IntegerField(default=0)),
                ('backlinks_concurency', models.IntegerField(default=0)),
                ('total_concurency', models.FloatField(default=0)),
                ('direct_upscale', models.FloatField(default=0)),
                ('seo_concurency', models.IntegerField(default=0)),
                ('direct_concurency', models.IntegerField(default=0)),
                ('status', models.CharField(default='progress', max_length=100)),
                ('views', models.IntegerField(default=0)),
                ('average_age', models.IntegerField(default=0)),
                ('average_volume', models.IntegerField(default=0)),
                ('average_total_backlinks', models.IntegerField(default=0)),
                ('average_unique_backlinks', models.IntegerField(default=0)),
                ('vital_sites', models.CharField(default='', max_length=150)),
                ('vital_sites_count', models.SmallIntegerField(default=0)),
                ('is_direct_final', models.SmallIntegerField(default=0)),
                ('region', models.ForeignKey(default=255, on_delete=django.db.models.deletion.DO_NOTHING, to='main.region')),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('balance', models.FloatField(default=0)),
                ('orders_amount', models.IntegerField(default=0)),
                ('ordered_keywords', models.IntegerField(default=0)),
                ('region', models.ForeignKey(default=255, on_delete=django.db.models.deletion.DO_NOTHING, to='main.region')),
            ],
        ),
        migrations.CreateModel(
            name='TicketPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('order', models.SmallIntegerField(default=0)),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='pending', max_length=15)),
                ('opened', models.DateTimeField(default=django.utils.timezone.now)),
                ('closed', models.DateTimeField(blank=True, null=True)),
                ('user_ticket_id', models.IntegerField(default=1)),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('posts', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ticketpost')),
            ],
        ),
        migrations.CreateModel(
            name='RequestQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_recheck', models.BooleanField(default=False)),
                ('region', models.ForeignKey(default=255, on_delete=django.db.models.deletion.DO_NOTHING, to='main.region')),
                ('request_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.request')),
            ],
        ),
        migrations.CreateModel(
            name='OrderData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField(null=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.request')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(default=0)),
                ('progress', models.SmallIntegerField(default=0)),
                ('ordered_keywords_amount', models.SmallIntegerField(default=0)),
                ('user_order_id', models.IntegerField(default=1)),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.orderdata')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HandledXml',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xml', models.TextField()),
                ('status', models.CharField(max_length=10)),
                ('refresh_timer', models.SmallIntegerField(default=10)),
                ('reruns_count', models.SmallIntegerField(default=0)),
                ('top_ads_count', models.SmallIntegerField(default=0)),
                ('bottom_ads_count', models.SmallIntegerField(default=0)),
                ('region', models.ForeignKey(default=255, on_delete=django.db.models.deletion.DO_NOTHING, to='main.region')),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.request')),
            ],
        ),
    ]
