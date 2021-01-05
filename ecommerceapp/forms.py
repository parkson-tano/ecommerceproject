from django import forms
from  .models import Order, Customer
from django.contrib.auth.models import User

class CheckOutForm(forms.ModelForm):
	class Meta:
		model = Order 
		fields = ['ordered_by', 'shipping_address',  'mobile', 'email']

class CustomerRegistrationForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput())
	password = forms.CharField(widget=forms.PasswordInput())
	email = forms.CharField(widget=forms.EmailInput())
	class Meta:
		model = Customer
		fields = ['username','password','email','full_name', 'address']

	
	# def clean_username(self):
	# 	uname = self.cleaned_data.get('username')
	# 	if User.objects.filter(username=uname).exists:
	# 		raise forms.ValidationError('this username already exists')
		
	# 	return uname

	# def clean_email(self):
	# 	emai = self.cleaned_data.get('email')
	# 	if User.objects.filter(email=emai).exists:
	# 		raise forms.ValidationError('this email already exists')
	# 	return emai

class CustomerLoginForm(forms.Form):
	username = forms.CharField(widget=forms.TextInput())
	password = forms.CharField(widget=forms.PasswordInput())