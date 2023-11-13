from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegisterForm(UserCreationForm):


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EditMyForm(forms.ModelForm):
    addrX = forms.CharField(max_length=10)
    addrY = forms.CharField(max_length=10)
    upsid = forms.CharField(max_length=10, required=False)

    class Meta:
        model = UserProfile
        fields = ['addrX', 'addrY', 'upsid']


class PlaceOrderForm(forms.ModelForm):
    addrX = forms.CharField(max_length=10)
    addrY = forms.CharField(max_length=10)
    upsid = forms.CharField(max_length=10, required=False)


    class Meta:
        model = UserProfile
        fields = ['addrX', 'addrY', 'upsid']

class addShoppingCartForm(forms.ModelForm):
    amount = forms.IntegerField(label="purchase amount:", min_value = 1)
    package_desc = forms.CharField(max_length=1000,required=False,label="pacakge description")
    addrX = forms.CharField(max_length=10, required=False,label="deleivery address X:")
    addrY = forms.CharField(max_length=10, required=False, label="deleivery address X:")
    upsid = forms.CharField(max_length=10, required=False, label="UPS_ID(optional):")

    class Meta:
        model = UserProfile
        fields = ['addrX','addrY','upsid']