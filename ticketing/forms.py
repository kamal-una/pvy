from django import forms
from django.forms import ModelForm
from ticketing.models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import ugettext, ugettext_lazy as _


class UserForm(ModelForm):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'title', 'first_name', 'last_name', 'address1', 'address2', 'address3', 'city', 'country', 'post_code']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-4'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class="col-sm-offset-4 btn-success"))
        super(UserForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user