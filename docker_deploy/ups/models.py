from django.db import models
from django.contrib.auth.models import User
from model_utils.fields import StatusField
from model_utils import Choices

# Create your models here.

class Truck(models.Model):
    truck_id = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()
    STATUS = Choices('idle', 'go pickup', 'arrive wharehouse', 'delivering', 'delivered') 
    t_status = StatusField()
    def __str__(self):
        return ", status: " + self.t_status

    class Meta:
        managed = False
        db_table = 'truck'


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    upsaccount = models.CharField(max_length=100)
    dest_x = models.IntegerField()
    dest_y = models.IntegerField()
    def __str__(self):
        return self.order_id + ", dest_x: " + self.dest_x + ", dest_y: " + self.dest_y
    
    class Meta:
        managed = False
        db_table = 'orders' 

class Delivery(models.Model):
    package_id = models.IntegerField(primary_key=True)
    # can access all the deliveries own by the order by order.deliveries.all()
    order = models.ForeignKey(Order, related_name='deliveries', on_delete=models.CASCADE) 
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    dest_x = models.IntegerField()
    dest_y = models.IntegerField()
    descr = models.CharField(max_length=300)
    STATUS = Choices('ready', 'delivering', 'delivered') 
    d_status = StatusField()
    
    def __str__(self):
        return self.package_id + ", status: " + self.d_status

    class Meta:
        managed = False
        db_table = 'delivery'