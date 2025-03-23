from django import forms
from .models import ShippingAddress
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Initialize Crispy Forms helper
    self.helper = FormHelper()
    self.helper.form_method = 'post'
    self.helper.layout = Layout(
        Row(
            Column('full_name', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('address_line1', css_class='form-group col-md-6 mb-0'),
            Column('address_line2', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('city', css_class='form-group col-md-6 mb-0'),
            Column('county', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('postal_code', css_class='form-group col-md-6 mb-0'),
            Column('country', css_class='form-group col-md-6 mb-0'),
            css_class='form-row'
        ),
        Submit('submit', 'Submit Shipping Details', css_class='btn btn-primary')
    )


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update({"class": "form-control", "id": "full_name", "placeholder": "Full Name"})
        self.fields["address_line1"].widget.attrs.update({"class": "form-control", "id": "address_line1", "placeholder": "Address Line 1"})
        self.fields["address_line2"].widget.attrs.update({"class": "form-control", "id": "address_line2", "placeholder": "Address Line 2"})
        self.fields["city"].widget.attrs.update({"class": "form-control", "id": "city", "placeholder": "City"})
        self.fields["postal_code"].widget.attrs.update({"class": "form-control", "id": "postal_code", "placeholder": "Postal Code"})
        self.fields["county"].widget.attrs.update({"class": "form-control", "id": "county", "placeholder": "County"})
        self.fields["country"].widget.attrs.update({"class": "form-control", "id": "country", "placeholder": "Country"})
        self.fields["phone"].widget.attrs.update({"class": "form-control", "id": "phone", "placeholder": "Phone Number"})
