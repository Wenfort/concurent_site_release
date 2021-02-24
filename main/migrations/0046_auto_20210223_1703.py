# Generated by Django 3.1.5 on 2021-02-23 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_auto_20210219_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.orderstatus'),
        ),
        migrations.AlterField(
            model_name='order',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.request'),
        ),
    ]
