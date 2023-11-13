from django.contrib import admin

from .models import ORDER,Product,Package
# Register your models here.

admin.site.register(Product)
admin.site.register(ORDER)
admin.site.register(Package)