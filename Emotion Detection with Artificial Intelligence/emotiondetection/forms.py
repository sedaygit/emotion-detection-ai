#what a person have: age, first and last name etc.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from .models import UploadedImage, AnalysisResult

#create/register a user(model form)
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        #password1 is the password we wanna choose
        #password2 is for verification

#authenticate a user (model form)  
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())   

class ImageUploadForm(forms.ModelForm):
   class Meta:
       model = UploadedImage
       fields = ['image']  
       exclude = ['registered_user']

class ResultForm(forms.ModelForm):
    class Meta:
        model = AnalysisResult 
        fields = ['detected_image'] 
        exclude = ['detected_image']       

