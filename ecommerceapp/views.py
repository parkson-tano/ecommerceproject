from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm, PasswordResetForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  TemplateView, View)
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib import messages
from .forms import *
from .models import *
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
# Create your views here.
class EcoMixin(object):

	def dispatch(self, request, *args, **kwargs):

		cart_id = request.session.get('cart_id')
		if cart_id:
			cart_obj = Cart.objects.get(id=cart_id)
			if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
				cart_obj.customer = request.user.customer
				cart_obj.save()
		return  super().dispatch(request, *args, **kwargs)

class IndexView(EcoMixin,TemplateView):
	template_name = 'index.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['name'] = 'Parkson tano daniel'
		all_product = Product.objects.all().order_by('-id')
		paginator = Paginator(all_product, 8)
		page_number = self.request.GET.get('page')
		product_list = paginator.get_page(page_number)
		context['product_list'] = product_list
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
		cart_obj.save()

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
		if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
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
			
			pm =  form.cleaned_data.get('payment_method')
			order = form.save()
			if pm == 'Khalti':
				return redirect(reverse('ecommerceapp:paymentrequest') + "?o_id="+ str(order.id))
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

class PaymentRequestView(View):
	def get(self,request, *args, **kwargs):
		#context = super().get_context_data(**kwargs)
		o_id = request.GET.get('o_id')
		order = Order.objects.get(id=o_id)
		context= {
			'order' : order
		} 
		return render(request, 'paymentrequest.html', context)

class PaymentVerifyView(View):
	def get(self, request, *args, **kwargs):
		data = {

		}

		return JsonResponse(data)

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
		# login(self.request, user)
		returnVal =  super().form_valid(form)
		send_email(user)
		return returnVal

class CustomerLoginView(FormView):
	template_name = 'customerlogin.html'
	form_class =  CustomerLoginForm
	success_url = reverse_lazy('ecommerceapp:index')

	def form_valid(self, form):
		uname = form.cleaned_data.get('username')
		pword = form.cleaned_data.get('password')
		usr = authenticate(username=uname, password=pword)
		if usr is not None and Customer.objects.filter(user=usr).exists():
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
@login_required
def passwordchange(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password change')
            return redirect('ecommerceapp:customerprofile')
        else:
            return render(request, 'forgotpassword/password_change.html', {'form':form})
    else:
        form = PasswordChangeForm(request.user)
        return render(request, 'forgotpassword/password_change.html', {'form':form})

def password_reset_request(request):
    password_reset_form = PasswordResetForm()
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "forgotpassword/reset_subject.txt"
                    c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request, 'A message has been sent to your email')
                    return redirect ("/")
            messages.error(request, 'Email address in invalid')
            return render(request=request, template_name="forgotpassword/password_reset.html", context={"password_reset_form":password_reset_form})
    return render(request=request, template_name="forgotpassword/password_reset.html", context={"password_reset_form":password_reset_form})
class CustomerLogoutView(View):
	
	def get(self, request):
		logout(request)
		return redirect('ecommerceapp:index')

class CustomerProfileView(TemplateView):
	template_name = 'customerprofile.html'


	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
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
		if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
			order_id = self.kwargs['pk']
			order = Order.objects.get(id=order_id)

			action = request.GET.get('action')
			ord_obj = Order.objects.get(id=order_id)
			order_obj = ord_obj.cart
			if action == 'rmv':
				order_obj.save()
				order_obj.delete()
				return redirect('ecommerceapp:customerprofile')
			else:
				pass

			if request.user.customer != order.cart.customer:
				return redirect('ecommerceapp:customerprofile')
			else:
				pass
		else:
			return redirect('/login/?next=/profile/')


		return super().dispatch(request, *args, **kwargs)

		
class SearchView(TemplateView):
	template_name = 'search.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		kw = self.request.GET['keyword']
		results = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw))
		context['results'] = results 
		return context

### ---------admin class----------
class AdminLoginView(FormView):
	template_name = 'adminpages/adminlogin.html'
	form_class = CustomerLoginForm
	success_url = reverse_lazy('ecommerceapp:adminhome')
	def form_valid(self, form):
		uname = form.cleaned_data.get('username')
		pword = form.cleaned_data.get('password')
		usr = authenticate(username=uname, password=pword)
		if usr is not None and Admin.objects.filter(user=usr).exists():
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

class AdminRequiredMixin(object):
	def dispatch(self, request, *args, **kwargs):
		if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
			pass
		else:
			return redirect('/admin-login')

		return super().dispatch(request, *args, **kwargs)

class AdminHomeView(AdminRequiredMixin, TemplateView):
	template_name = 'adminpages/adminhome.html'

	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    context['pendingorders'] = Order.objects.filter(order_status = 'Order Recieved')

	    return context

class AdminOrderView(AdminRequiredMixin, DetailView):

	template_name = 'adminpages/adminorderdetails.html'
	model = Order
	context_object_name = 'ord_obj'
	def get_context_data(self, **kwargs):
	    context = super().get_context_data(**kwargs)
	    context['allstatus'] = ORDER_STATUS
	    return context

class AdminOrderListView(AdminRequiredMixin, ListView):
	template_name = 'adminpages/adminlistorder.html'
	queryset = Order.objects.all().order_by('-id')
	context_object_name = 'allorders'

class AdminOrderStatusChangeView(AdminRequiredMixin, View):
	def post(self, request, *arg, **kwargs):
		order_id = self.kwargs['pk']
		order_obj = Order.objects.get(id=order_id)
		new_status = request.POST.get('status')
		order_obj.order_status = new_status
		order_obj.save()
		return redirect(reverse_lazy('ecommerceapp:adminorderdetail', kwargs={'pk': order_id}))

class AdminLogoutView(View):
	
	def get(self, request):
		logout(request)
		return redirect('ecommerceapp:adminhome')	

class AdminProductListView(AdminRequiredMixin, ListView):
	template_name = 'adminpages/adminproductlist.html'
	queryset = Product.objects.all().order_by('-id')
	context_object_name = 'allproducts'

class AdminManageProductView(AdminRequiredMixin, View):
	
	def get(self, request, **kwargs):
		p_id = self.kwargs['p_id']
		action = request.GET.get('action')
		p_obj = Product.objects.get(id=p_id)
		p_obj.save()	

		if action == 'rmv':
			p_obj.save()
			p_obj.delete()
		else:
			pass
		return redirect('ecommerceapp:adminproductlist')
class AdminProductCreateView(AdminRequiredMixin, CreateView):
	template_name = 'adminpages/adminproductcreate.html'
	form_class = ProductForm
	success_url = reverse_lazy('ecommerceapp:adminproductlist')

	def form_valid(self, form):
		p = form.save()
		images = self.request.FILES.getlist('more_images')
		for i in images:
			ProductImage.objects.create(product=p, image=i)
		return super().form_valid(form)

class AdminProductEditView(AdminRequiredMixin, UpdateView):
	template_name = 'adminpages/adminproductedit.html'
	model = Product
	success_url = reverse_lazy('ecommerceapp:adminproductlist')
	fields = ['title','slug','category','image', 'marked_price',
		'selling_price', 'description', 'warranty', 'return_policy']

class AdminProductdeleteView(AdminRequiredMixin, DeleteView):
	template_name = 'adminpages/product_confirm_delete.html'
	model = Product
	success_url = reverse_lazy('ecommerceapp:adminproductlist')