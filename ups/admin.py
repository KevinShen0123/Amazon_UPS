from django.contrib import admin

# Register your models here.
from .models import Truck
from .models import Package
from .models import Shipment

# Register your models here.
admin.site.register(Truck)
admin.site.register(Package)
admin.site.register(Shipment)

