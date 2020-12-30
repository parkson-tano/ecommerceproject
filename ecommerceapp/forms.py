from django.forms import ModelForm
from  .models import Order 


class CheckOutForm(ModelForm):
	class Meta:
		model = Order 
		fields = ['ordered_by', 'shipping_address',  'mobile', 'email']