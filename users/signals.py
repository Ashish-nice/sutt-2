from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, AdminProfile, LibrarianProfile, StudentProfile

@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'admin':
            AdminProfile.objects.create(user=instance)
        elif instance.user_type == 'librarian':
            LibrarianProfile.objects.create(user=instance)
        elif instance.user_type == 'student':
            StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    if instance.user_type == 'admin':
        instance.adminprofile.save()
    elif instance.user_type == 'librarian':
        instance.librarianprofile.save()
    elif instance.user_type == 'student':
        instance.studentprofile.save()
