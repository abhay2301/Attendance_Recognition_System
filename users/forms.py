from django import forms
from django.contrib.auth.forms import UserCreationForm

from face_app.models import FaceImage

from .models import CustomUser

class StudentRegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'student_id',
            'email',
            'department',
            'semester',
            'password'
        ]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'user_type', 'student_id', 'department', 'phone']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'department', 'phone']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
        
class FaceImageUploadForm(forms.ModelForm):
    image = forms.ImageField()
    class Meta:
        model = FaceImage
        fields = ['image']
        
        
class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)