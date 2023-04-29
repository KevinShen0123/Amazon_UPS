# Generated by Django 4.1.5 on 2023-04-29 23:18

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('package_id', models.IntegerField(primary_key=True, serialize=False)),
                ('dest_x', models.IntegerField()),
                ('dest_y', models.IntegerField()),
                ('descr', models.CharField(max_length=300)),
                ('d_status', model_utils.fields.StatusField(choices=[('ready', 'ready'), ('delivering', 'delivering'), ('delivered', 'delivered')], default='ready', max_length=100, no_check_for_status=True)),
            ],
            options={
                'db_table': 'delivery',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.IntegerField(primary_key=True, serialize=False)),
                ('upsaccount', models.CharField(max_length=100)),
                ('dest_x', models.IntegerField()),
                ('dest_y', models.IntegerField()),
            ],
            options={
                'db_table': 'orders',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.IntegerField()),
                ('od_status', models.CharField(max_length=300)),
                ('m_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'order_status',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('truck_id', models.IntegerField(primary_key=True, serialize=False)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('t_status', model_utils.fields.StatusField(choices=[('idle', 'idle'), ('go pickup', 'go pickup'), ('arrive wharehouse', 'arrive wharehouse'), ('delivering', 'delivering'), ('delivered', 'delivered')], default='idle', max_length=100, no_check_for_status=True)),
            ],
            options={
                'db_table': 'truck',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WareHouse',
            fields=[
                ('whid', models.IntegerField(primary_key=True, serialize=False)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
            ],
            options={
                'db_table': 'warehouse',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DeliveryProof',
            fields=[
                ('delivery', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='ups.delivery')),
                ('proof', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deliveries', models.ManyToManyField(blank=True, to='ups.delivery')),
                ('truck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='driver', to='ups.truck')),
            ],
        ),
    ]
