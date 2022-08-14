from enum import unique
from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from autoslug import AutoSlugField
# Create your models here.

class Admin(models.Model):
	user = models.OneToOneField(User, on_delete= models.CASCADE)
	full_name = models.CharField(max_length=250)
	mobile = models.CharField(max_length=20)
	image = models.ImageField(upload_to='admins')

	def __str__(self):
		return self.user.username
ACC_TYPE = (
	('buyer', 'Buyer'),
	('seller', 'Seller')
)

class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=300, null=True,  blank=True)
	quater = models.CharField(max_length=200, null=True,  blank=True)
	country = models.CharField(max_length=100, null=True,  blank=True)
	region = models.CharField(max_length=256, null=True,  blank=True)
	town = models.CharField(max_length=256, null=True,  blank=True)
	store_address = models.CharField(max_length=256, null=True,  blank=True)
	phone_number = models.IntegerField(null=True,  blank=True)
	verified = models.BooleanField(default=False)
	account_type = models.CharField(max_length=256, choices=ACC_TYPE, default='buyer')
	joined_on = models.DateTimeField(auto_now_add=True)
	
class Category(models.Model):
	title = models.CharField(max_length=200)
	slug = AutoSlugField(populate_from='title', unique=True)

	def __str__(self):
		return self.title



class Product(models.Model):
	seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	# seller_type = models.CharField(max_length=156, choices=ACC_TYPE,  default="personal")
	title = models.CharField(max_length=200)
	category =models.ForeignKey(Category, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='products')
	marked_price = models.PositiveIntegerField()
	selling_price = models.PositiveIntegerField()
	description = models.TextField()
	quantity = models.IntegerField(default=0)
	town = models.CharField(max_length=256, null=True, blank=True)
	warranty = models.CharField(max_length=300, null=True, blank = True)
	return_policy = models.CharField(max_length=300, null=True, blank=True)
	contact = models.BigIntegerField(null=True, blank=True)
	view_count = models.PositiveIntegerField(default=0)
	date_created = models.DateTimeField(default=now)
	slug = AutoSlugField(
		populate_from=lambda instance: instance.title,
                         unique_with=['seller__customer__first_name', 'date_created__month'],
                         slugify=lambda value: value.replace(' ','-')
	)


	def __str__(self):
		return self.title

class ProductImage(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='products.image/')

	def __str__(self):
		return self.product.title
	

class  Cart(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	total = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Cart: {str(self.id)}"
class CartProduct(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	rate = models.PositiveIntegerField(default=1)
	quantity = models.PositiveIntegerField(default=1)
	subtotal = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"Cart: {str(self.cart.id)} CartProduct {str(self.id)}"

ORDER_STATUS = (
		('Order Recieved', 'Order Recieved'),
		('Order Processing',  'Order Processing'),
		('On the way', 'On the way'),
		('Order Complete', 'Order Complete'),
		('Order Cancel', 'Order Cancel'),
	)

METHOD = (
	("Cash On Delivery", "Cash On Delivery"),
	('Mobile Money', 'Mobile Money'),

)
class Order(models.Model):
	cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
	ordered_by = models.CharField(max_length=200)
	shipping_address  = models.CharField(max_length=200)
	mobile = models.CharField(max_length=10)
	email = models.EmailField(null=True, blank=True)
	subtotal = models.PositiveIntegerField()
	discount = models.PositiveIntegerField()
	total = models.PositiveIntegerField()
	order_status = models.CharField(max_length=50, choices=ORDER_STATUS, default='Order Recieved')
	created_at = models.DateTimeField(auto_now_add=True)
	payment_method = models.CharField(max_length = 20, choices=METHOD, default='Cash On Delivery')
	payment_completed = models.BooleanField(default=False, null=True, blank=True)

	def __str__(self):
		return f"Order: {str(self.id)}"