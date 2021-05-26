# Generated by Django 3.1.7 on 2021-05-26 10:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_auto_20210525_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdata',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, to='auth.user'),
            preserve_default=False,
        ),
    ]
