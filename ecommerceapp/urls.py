from django.urls import path
from .views import *

app_name = 'ecommerceapp'

urlpatterns = [
	path('', IndexView.as_view(), name = 'index'),
	path('about/', AboutView.as_view(), name='about'),
	path('contact/', ContactView.as_view(), name='contact'),
	path('all-product', AllProductsView.as_view(), name='allproduct'),
	path('product/<slug:slug>/', ProductDetailsView.as_view(), name='productdetail'),
]
