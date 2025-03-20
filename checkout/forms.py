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
            Column('address_line_1', css_class='form-group col-md-6 mb-0'),
            Column('address_line_2', css_class='form-group col-md-6 mb-0'),
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
        fields = ["full_name", "address_line_1", "address_line_2", "city", "postal_code", "county", "country", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.update({"class": "form-control", "placeholder": "Full Name"})
        self.fields["address_line_1"].widget.attrs.update({"class": "form-control", "placeholder": "Address Line 1"})
        self.fields["address_line_2"].widget.attrs.update({"class": "form-control", "placeholder": "Address Line 2"})
        self.fields["city"].widget.attrs.update({"class": "form-control", "placeholder": "City"})
        self.fields["postal_code"].widget.attrs.update({"class": "form-control", "placeholder": "Postal Code"})
        self.fields["county"].widget.attrs.update({"class": "form-control", "placeholder": "County"})
        self.fields["country"].widget.attrs.update({"class": "form-control", "placeholder": "Country"})
        self.fields["phone"].widget.attrs.update({"class": "form-control", "placeholder": "Phone Number"})
