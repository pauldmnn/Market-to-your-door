from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ["full_name", "address", "city", "postal_code", "country", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update({"class": "form-control", "placeholder": "Full Name"})
        self.fields["address"].widget.attrs.update({"class": "form-control", "placeholder": "Street Address"})
        self.fields["city"].widget.attrs.update({"class": "form-control", "placeholder": "City"})
        self.fields["postal_code"].widget.attrs.update({"class": "form-control", "placeholder": "Postal Code"})
        self.fields["country"].widget.attrs.update({"class": "form-control", "placeholder": "Country"})
        self.fields["phone"].widget.attrs.update({"class": "form-control", "placeholder": "Phone Number"})
