from django.contrib import admin

# Register your models here.
from .models import Truck
from .models import Order
from .models import Delivery

# Register your models here.
admin.site.register(Truck)
admin.site.register(Order)
admin.site.register(Delivery)

