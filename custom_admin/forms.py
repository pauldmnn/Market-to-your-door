from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from checkout.models import Order
from products.models import Product, Category
from django.contrib.auth.models import User


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'payment_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field('status'),
            Field('payment_id'),
            Submit('submit', 'Update Order', css_class='btn btn-primary w-100')
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'inventory', 'category', 'image', 'slug']
        widgets = {
            'slug': forms.TextInput(attrs={'readonly': True}) 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field('name'),
            Field('description'),
            Field('price'),
            Field('inventory'),
            Field('category'),
            Field('image'),
            Field('slug'),
            Submit('submit', 'Save Product', css_class='btn btn-primary w-100')
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field('name'),
            Field('slug'),
            Submit('submit', 'Save Category', css_class='btn btn-primary w-100')
        )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']