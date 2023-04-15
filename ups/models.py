from django.db import models
from django.contrib.auth.models import User
from model_utils.fields import StatusField
from model_utils import Choices

# Create your models here.

class Truck(models.Model):
    STATUS = Choices('available', 'pickingup', 'delivering') 
    status = StatusField()
    def __str__(self):
        return self.id + ", status: " + self.status


class Package(models.Model):
    truck_id = models.ForeignKey(Truck, on_delete=models.CASCADE)
    dest_x = models.IntegerField()
    dest_y = models.IntegerField()
    def __str__(self):
        return self.id + ", dest_x: " + self.dest_x + ", dest_y: " + self.dest_y 

class Shipment(models.Model):
    truck_id = models.ForeignKey(Truck, on_delete=models.CASCADE)
    package = models.OneToOneField(Package, on_delete=models.CASCADE)
    STATUS = Choices('pickedup', 'delivering', 'delivered') 
    status = StatusField()
    def __str__(self):
        return self.id + ", status: " + self.status