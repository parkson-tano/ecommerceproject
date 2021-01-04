from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
import random 
# Create your views here.

class IndexView(TemplateView):
	template_name = 'index.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['name'] = 'Parkson tano daniel'
		context['product_list'] = Product.objects.all().order_by('-id')
		return context

class AboutView(TemplateView):
	template_name = 'about.html'

class ContactView(TemplateView):
	template_name = 'contact.html'

class AllProductsView(TemplateView):
	template_name = 'allproduct.html'

	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    context['allcategories'] = Category.objects.all().order_by('title')

	    return context

class ProductDetailsView(TemplateView):
	template_name = 'productdetails.html'
	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    url_slug =  kwargs['slug']
	    product = Product.objects.get(slug=url_slug)
	    product.view_count += 1
	    product.save()
	    context['product'] = product
	    return context
	
class AddToCartView(TemplateView):
	template_name = 'addtocart.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
	    #get product id from requeted url
		product_id = self.kwargs['pro_id']
	    #get product
		product_obj = Product.objects.get(id=product_id)

		#check if cart exist
		cart_id = self.request.session.get('cart_id', None)

		if cart_id:
			cart_obj = Cart.objects.get(id=cart_id)
			this_product_in_cart = cart_obj.cartproduct_set.filter(product = product_obj)
			#items  in cart already
			if this_product_in_cart.exists():
				cartproduct = this_product_in_cart.last()
				cartproduct.quantity += 1
				cartproduct.subtotal += product_obj.selling_price
				cartproduct.rate = product_obj.selling_price
				cartproduct.save()
				cart_obj.total += product_obj.selling_price
				cart_obj.save()

			#new item 
			else:
				cartproduct = CartProduct.objects.create(
					cart = cart_obj, product=product_obj, subtotal=product_obj.selling_price, rate=product_obj.selling_price)
				cart_obj.total += product_obj.selling_price
				cart_obj.save()
		else:
			cart_obj = Cart.objects.create(total=0)
			self.request.session['cart_id'] = cart_obj.id
			cartproduct = CartProduct.objects.create(
					cart = cart_obj, product=product_obj, subtotal=product_obj.selling_price, rate=product_obj.selling_price)
			cart_obj.total += product_obj.selling_price
			cart_obj.save()
		#check if product already exist in cart
		return context

class MyCartView(TemplateView):
	template_name = 'mycart.html'

	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    cart_id = self.request.session.get('cart_id', None)

	    if cart_id:
	    	cart = Cart.objects.get(id=cart_id)
	    else:
	    	cart = None
	    context['cart'] = cart
	    return context

class ManageCartView(View):
	def get(self, request, **kwargs):
		c_id = self.kwargs['c_id']
		action = request.GET.get('action')
		c_obj = CartProduct.objects.get(id=c_id)
		cart_obj = c_obj.cart

		if action == 'inc':
			c_obj.quantity += 1
			c_obj.subtotal += c_obj.rate
			c_obj.save()
			cart_obj.total += c_obj.rate
			cart_obj.save()

		elif action == 'dcr':
			if c_obj.quantity > 0:
				c_obj.quantity -= 1
				c_obj.subtotal -= c_obj.rate
				c_obj.save()
				cart_obj.total -= c_obj.rate
				cart_obj.save()
			else:
				c_obj.delete()	

		elif action == 'rmv':
			cart_obj.total -= c_obj.subtotal
			cart_obj.save()
			c_obj.delete()
		else:
			pass
		return redirect('ecommerceapp:mycart')

class EmptyCartView(View):

	def get(self, request, **kwargs):
		cart_id = request.session.get('cart_id', None)

		if cart_id:
			cart = Cart.objects.get(id=cart_id)
			cart.cartproduct_set.all().delete()
			cart.total = 0
			cart.save()

		return redirect('ecommerceapp:mycart')


class CheckOutView(CreateView):
	template_name = 'checkout.html'
	form_class = CheckOutForm
	success_url = reverse_lazy('ecommerceapp:index')
	#@method_decorator(csrf_exempt)
	def form_valid(self, form):
		cart_id = self.request.session.get('cart_id')
		if cart_id:
			cart_obj = Cart.objects.get(id=cart_id)
			form.instance.cart = cart_obj
			form.instance.subtotal = cart_obj.total
			form.instance.discount = 0
			form.instance.total = cart_obj.total
			form.instance.order_status = 'Order_Recieved'

			del self.request.session['cart_id']
		else:
			return redirect('ecommerceapp:index')

		return super().form_valid(form)

	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    cart_id = self.request.session.get('cart_id', None)

	    if cart_id:
	    	cart_obj = Cart.objects.get(id=cart_id)

	    else:
	    	cart_obj = None

	    context['cart'] = cart_obj

	    return context

class CustomerRegistrationView(CreateView):
	template_name = 'customerregistration.html'
	form_class =  CustomerRegistrationForm
	success_url = reverse_lazy('ecommerceapp:index')

	def form_valid(self, form):
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')
		email = form.cleaned_data.get('email')

		user = User.objects.create_user(username, email, password)
		form.instance.user = user
		return super().form_valid(form)

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=uname).exists:
			raise forms.ValidationError('this username already exists')
		
		return uname

