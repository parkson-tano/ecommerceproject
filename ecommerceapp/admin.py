from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([Category, Cart, Product, CartProduct, Order, Admin, ProductImage])


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    # list_filter = ('full_name',)

admin.site.register(Customer, CustomerAdmin)
