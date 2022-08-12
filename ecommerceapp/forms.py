from django import forms
from  .models import Order, Customer, Product
from django.contrib.auth.models import User

class CheckOutForm(forms.ModelForm):
	class Meta:
		model = Order 
		fields = ['ordered_by', 'shipping_address',  'mobile', 'email', 'payment_method']

class CustomerRegistrationForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput())
	password = forms.CharField(widget=forms.PasswordInput())
	email = forms.CharField(widget=forms.EmailInput())
	class Meta:
		model = Customer
		fields = "__all__"

	
	def clean_username(self):
		uname = self.cleaned_data.get('username')
		if User.objects.filter(username=uname).exists():
			raise forms.ValidationError('this username already exists')
		
		return uname

	def clean_email(self):
		emai = self.cleaned_data.get('email')
		if User.objects.filter(email=emai).exists():
			raise forms.ValidationError('this email already exists')
		return emai

class CustomerLoginForm(forms.Form):
	username = forms.CharField(widget=forms.TextInput())
	password = forms.CharField(widget=forms.PasswordInput())

class ProductForm(forms.ModelForm):

	more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={
		'class': 'form-control',
		'multiple': True
	}))
	class Meta:
		model = Product
		fields = ['title','category','image', 'marked_price',
		'selling_price', 'description', 'warranty', 'return_policy']

		widgets = {
			"title": forms.TextInput(attrs= { 
				'placeholder': 'Enter the Product Title'
			}),
			"marked_price": forms.NumberInput(attrs= { 
				'placeholder': 'Enter the Marked_Price'
			}),
			"selling_price": forms.NumberInput(attrs= { 
				'placeholder': 'Enter the Selling Price'
			}),
			"description": forms.Textarea(attrs= { 
			'placeholder': 'Enter the Product Description',
			'rows': 5
		
			}),
			"warranty": forms.TextInput(attrs= { 
				'placeholder': 'Enter the Product Warranty'
			}),
				"return_policy": forms.TextInput(attrs= { 
				'placeholder': 'Enter the Product return policy'
			}),
			"image": forms.FileInput(attrs= { 
				'class':'form-control'
			}),

		}