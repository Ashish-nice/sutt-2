from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.conf import settings
from PIL import Image
from django.core.exceptions import ValidationError

# Create your models here

def validate_single_profile(user):
    """Ensure user has only one type of profile"""
    profiles = []
    if hasattr(user, 'studentprofile'):
        profiles.append('student')
    if hasattr(user, 'librarianprofile'):
        profiles.append('librarian')
    if hasattr(user, 'adminprofile'):
        profiles.append('admin')
    
    if len(profiles) > 1:
        raise ValidationError(f"User cannot have multiple profiles: {', '.join(profiles)}")

class AdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    def __str__(self):
        return f'{self.user.username} Profile'
    def save(self,*args, **kwargs):
        is_new = self._state.adding
        validate_single_profile(self.user)
        # Only update user type if this is a new profile or user type is different
        if is_new and not self.user.is_superuser and self.user.user_type != 'admin':
            self.user.user_type = 'admin'
            self.user.save(update_fields=['user_type'])
        super().save(*args, **kwargs)
        # Resize image
        if self.image and hasattr(self.image, 'path'):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)

class LibrarianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    def __str__(self):
        return f'{self.user.username} Profile'
    def save(self,*args, **kwargs):
        is_new = self._state.adding
        validate_single_profile(self.user)
        if is_new and self.user.user_type != 'librarian':
            self.user.user_type = 'librarian'
            self.user.save(update_fields=['user_type'])
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
    psrn = models.CharField(max_length=100)

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    hostel = models.CharField(max_length=50)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    def __str__(self):
        return f'{self.user.username} Profile'
    def save(self,*args, **kwargs):
        is_new = self._state.adding
        validate_single_profile(self.user)
        if is_new and self.user.user_type != 'student':
            self.user.user_type = 'student'
            self.user.save(update_fields=['user_type'])
        super().save(*args, **kwargs)
        if self.image and hasattr(self.image, 'path'):
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
    
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')