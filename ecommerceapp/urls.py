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
	path('payment-request/', PaymentRequestView.as_view(), name='paymentrequest'),
	path('payment-verify/', PaymentVerifyView.as_view(), name='paymentverify'),

	path('register/', CustomerRegistrationView.as_view(), name='customerregistration'),
	path('login/', CustomerLoginView.as_view(), name='customerlogin'),
	path('logout/', CustomerLogoutView.as_view(), name='customerlogout'),

	path('profile/', CustomerProfileView.as_view(), name='customerprofile'),
	path('profile/order-<int:pk>', CustomerOrderDetailView.as_view(), name='customerorderdetails'),
	path('search/', SearchView.as_view(), name='search'),
	

	##admin view
	path('admin-login', AdminLoginView.as_view(), name='adminlogin'),
	path('admin-home', AdminHomeView.as_view(), name='adminhome'),
	path('admin-order/<int:pk>', AdminOrderView.as_view(), name='adminorderdetail'),
	path('admin-all-orders/', AdminOrderListView.as_view(), name='adminlistview'),
	path('admin-logout', AdminLogoutView.as_view(), name='adminlogout'),

	path('admin-order-<int:pk>-change/', AdminOrderStatusChangeView.as_view(), name='adminorderchange'),
	path('admin-product/list/',  AdminProductListView.as_view(), name='adminproductlist'),
	path('admin-product/add/', AdminProductCreateView.as_view(), name='admincreateproduct'),
]
