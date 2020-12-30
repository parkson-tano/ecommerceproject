from django.urls import path
from .views import *

app_name = 'ecommerceapp'

urlpatterns = [
	path('', IndexView.as_view(), name = 'index'),
	path('about/', AboutView.as_view(), name='about'),
	path('contact/', ContactView.as_view(), name='contact'),
	path('all-product', AllProductsView.as_view(), name='allproduct'),
	path('product/<slug:slug>/', ProductDetailsView.as_view(), name='productdetail'),
	path('add-to-cart-<int:pro_id>', AddToCartView.as_view(), name='addtocart'),

	path('my-cart', MyCartView.as_view(), name='mycart'),
	path('manage-cart/<int:c_id>', ManageCartView.as_view(), name='managecart'),
	path('empty-cart/', EmptyCartView.as_view(), name='emptycart'),
	path('checkout/', CheckOutView.as_view(), name='checkout'),
	

]
