from django.contrib import admin

from orders.models import Product, Order, OrderProduct

# Register your models here.

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderProduct)
