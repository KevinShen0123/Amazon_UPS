# Generated by Django 4.1.5 on 2023-04-29 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ups', '0003_warehouse_deliveryproof_driver'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='driver',
        ),
        migrations.AddField(
            model_name='driver',
            name='driver_id',
            field=models.IntegerField(default=0, primary_key=True, serialize=False),
        ),
    ]