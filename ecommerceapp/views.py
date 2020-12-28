from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *
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
		