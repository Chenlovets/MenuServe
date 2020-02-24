from django import forms 
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class SignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username','password2']:
            self.fields[fieldname].help_text = None

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)

    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class EditProfileForm(UserChangeForm):
    password = None

    class Meta:
        User = get_user_model()
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
        ) 

class MenuForm(forms.ModelForm): 
  
    class Meta: 
        model = Item 
        fields = ('item_category', 'item_name', 'item_price','item_image')

class StoreForm(forms.ModelForm): 
  
    class Meta: 
        model = Store
        fields = ('location', 'storeID')

class ManagerForm(forms.ModelForm):
    class Meta:
        model = Manager
        fields = ('location',)
        
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('location',)