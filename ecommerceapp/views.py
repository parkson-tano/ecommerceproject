from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView, FormView, DetailView
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.

class EcoMixin(object):

	def dispatch(self, request, *args, **kwargs):

		cart_id = request.session.get('cart_id')
		if cart_id:
			cart_obj = Cart.objects.get(id=cart_id)
			if request.user.is_authenticated and request.user.customer:
				cart_obj.customer = request.user.customer
				cart_obj.save()
		return  super().dispatch(request, *args, **kwargs)


class IndexView(EcoMixin,TemplateView):
	template_name = 'index.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['name'] = 'Parkson tano daniel'
		context['product_list'] = Product.objects.all().order_by('-id')
		return context

class AboutView(EcoMixin,TemplateView):
	template_name = 'about.html'

class ContactView(EcoMixin,TemplateView):
	template_name = 'contact.html'

class AllProductsView(EcoMixin,TemplateView):
	template_name = 'allproduct.html'

	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    context['allcategories'] = Category.objects.all().order_by('title')

	    return context

class ProductDetailsView(EcoMixin, TemplateView):
	template_name = 'productdetails.html'
	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    url_slug =  kwargs['slug']
	    product = Product.objects.get(slug=url_slug)
	    product.view_count += 1
	    product.save()
	    context['product'] = product
	    return context
	
class AddToCartView(EcoMixin,TemplateView):
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

class MyCartView(EcoMixin,TemplateView):
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

class ManageCartView(EcoMixin, View):
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

class EmptyCartView(EcoMixin,View):

	def get(self, request, **kwargs):
		cart_id = request.session.get('cart_id', None)

		if cart_id:
			cart = Cart.objects.get(id=cart_id)
			cart.cartproduct_set.all().delete()
			cart.total = 0
			cart.save()

		return redirect('ecommerceapp:mycart')


class CheckOutView(EcoMixin,CreateView):
	template_name = 'checkout.html'
	form_class = CheckOutForm
	success_url = reverse_lazy('ecommerceapp:index')
	#@method_decorator(csrf_exempt)

	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated and request.user.customer:
			pass
		else:
			return redirect('/login/?next=/checkout/')

		return super().dispatch(request, *args, **kwargs)

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
		login(self.request, user)
		return super().form_valid(form)

class CustomerLoginView(FormView):
	template_name = 'customerlogin.html'
	form_class =  CustomerLoginForm
	success_url = reverse_lazy('ecommerceapp:index')

	def form_valid(self, form):
		uname = form.cleaned_data.get('username')
		pword = form.cleaned_data.get('password')
		usr = authenticate(username=uname, password=pword)
		if usr is not None and usr.customer:
			login(self.request, usr)
		else:
			return render(self.request, self.template_name, {'form': self.form_class, 'error':'invalid creditials'})	


		return super().form_valid(form)

	def get_success_url(self):
		if 'next' in self.request.GET:
			next_url = self.request.GET.get('next')
			print(next_url)
			return next_url 	
		else:
			return self.success_url


class CustomerLogoutView(View):
	
	def get(self, request):
		logout(request)
		return redirect('ecommerceapp:index')

class CustomerProfileView(TemplateView):
	template_name = 'customerprofile.html'


	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated and request.user.customer:
			pass
		else:
			return redirect('/login/?next=/profile/')

		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    customer = self.request.user.customer
	    context['customer'] = customer	

	    orders = Order.objects.filter(cart__customer=customer).order_by('-id')
	    context['order'] = orders

	    return context
		
class CustomerOrderDetailView(DetailView):
	template_name = 'customerorderdetail.html'
	model = Order
	context_object_name = 'ord_obj'

	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated and request.user.customer:
			order_id = self.kwargs['pk']
			order = Order.objects.get(id=order_id)
			if request.user.customer != order.cart.customer:
				return redirect('ecommerceapp:customerprofile')
			else:
				pass
		else:
			return redirect('/login/?next=/profile/')

		return super().dispatch(request, *args, **kwargs)