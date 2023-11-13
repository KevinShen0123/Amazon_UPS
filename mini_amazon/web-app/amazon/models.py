from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#extends the file of user
class UserProfile(models.Model):
    userName = models.OneToOneField(User, on_delete=models.CASCADE)
    addrX = models.CharField(max_length=10, null=True)
    addrY = models.CharField(max_length=10, null=True)
    upsid = models.CharField(max_length=10, null=True)

    def get_absolute_url(self):
        return reverse('home')
   

class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_desc = models.CharField(max_length=100,null=True,unique=True)
    price = models.FloatField(max_length=100,blank=False)
    catalog = models.CharField(max_length=100)
    class Meta:
        db_table = 'product'


class ORDER(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_addr_x = models.IntegerField()
    order_addr_y = models.IntegerField()
    time = models.TimeField()
    order_owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True)

    upsid = models.CharField(max_length=10, null=True)
    price = models.FloatField(max_length=1000)

    class Meta:
        db_table = 'ORDER'


#one package only contains one kind of product
class Package(models.Model):
    package_id = models.AutoField(primary_key=True)
    package_desc =  models.CharField(max_length=100,null=True)
    package_owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True)
    amount = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    wh_id = models.IntegerField(null=True)
    order = models.ForeignKey(ORDER,on_delete=models.SET_NULL,null=True)
    STATUS_CHOICES = [
        ('OPEN','open'),
        ('PACKING', 'packing'),
        ('PACKED', 'packed'),
        ('LOADING', 'loading'),
        ('LOADED', 'loaded'),
        ('DELIVERING', 'delivering'),
        ('DELIVERED', 'delivered'),
    ]
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='open')

    class Meta:
        db_table = 'package'

