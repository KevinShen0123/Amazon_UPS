from django.db import models
from django.contrib.auth.models import User
from model_utils.fields import StatusField
from model_utils import Choices

# Create your models here.

class Truck(models.Model):

    x = models.IntegerField()
    y = models.IntegerField()
    STATUS = Choices('idle', 'go pickup', 'arrive wharehouse', 'delivering', 'delivered') 
    status = StatusField()
    def __str__(self):
        return self.id + ", status: " + self.status

    class Meta:
        managed = False
        db_table = 'truck'


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    upsaccount = models.CharField(max_length=100)
    dest_x = models.IntegerField()
    dest_y = models.IntegerField()
    def __str__(self):
        return self.id + ", dest_x: " + self.dest_x + ", dest_y: " + self.dest_y
    
    class Meta:
        managed = False
        db_table = 'order' 

class Delivery(models.Model):
    
    package_id = models.IntegerField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    truck_id = models.ForeignKey(Truck, on_delete=models.CASCADE)
    dest_x = models.IntegerField()
    dest_y = models.IntegerField()
    description = models.CharField(max_length=300)
    STATUS = Choices('ready', 'delivering', 'delivered') 
    status = StatusField()
    
    def __str__(self):
        return self.id + ", status: " + self.status

    class Meta:
        managed = False
        db_table = 'delivery'