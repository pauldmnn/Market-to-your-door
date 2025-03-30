from django import forms
from .models import CustomerQuestion


class ContactForm(forms.ModelForm):
    class Meta:
        model = CustomerQuestion
        fields = ['full_name', 'email', 'details']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
        }
