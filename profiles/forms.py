from django import forms
from .models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from allauth.account.forms import LoginForm



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # List the fields that users can update:
        fields = ['bio', 'phone', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('bio'),
            Field('phone'),
            Field('location'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary w-100')
        )


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the 'login' field's label so that it displays as "Email"
        self.fields['login'].label = "Email"
