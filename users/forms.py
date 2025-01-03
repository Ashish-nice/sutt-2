from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser, StudentProfile, LibrarianProfile, AdminProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('bits-pilani.ac.in'):
            raise forms.ValidationError("Please use your college email address (eg. user@pilani.bits-pilani.ac.in).")
        return email
    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

class AdminProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['image']

# Librarian Profile Update Form
class LibrarianProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = LibrarianProfile
        fields = ['psrn','image']

# Student Profile Update Form
class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['room_number', 'hostel','image']

class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    psrn = forms.CharField(max_length=100, required=False)
    room_number = forms.CharField(max_length=10, required=False)
    hostel = forms.CharField(max_length=50, required=False)

    class Meta:
        model = AdminProfile  # Default model
        fields = ['image']  # Default field

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user and hasattr(user, f'{user.user_type}profile'):
            self._meta.model = globals()[f"{user.user_type.title()}Profile"]
            self.instance = getattr(user, f'{user.user_type}profile')

        super().__init__(*args, **kwargs)

        # Show/hide fields based on user type
        if user:
            if user.is_superuser or user.user_type == 'admin':
                self.fields = {'image': self.fields['image']}
            elif user.user_type == 'librarian':
                self.fields = {
                    'psrn': self.fields['psrn'],
                    'image': self.fields['image']
                }
            elif user.user_type == 'student':
                self.fields = {
                    'room_number': self.fields['room_number'],
                    'hostel': self.fields['hostel'],
                    'image': self.fields['image']
                }
