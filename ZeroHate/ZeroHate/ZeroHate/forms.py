from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserCreationForm(UserCreationForm):
    """Custom form for user registration."""
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        # Add custom classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].help_text = None

class CustomAuthenticationForm(AuthenticationForm):
    """Custom form for user authentication."""
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        # Add custom classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'