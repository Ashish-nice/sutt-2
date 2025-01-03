from django.contrib import admin
from django.conf import settings
from .models import AdminProfile, LibrarianProfile, StudentProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'psrn')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_number', 'hostel')

@admin.action(description='Change user to librarian')
def change_user_to_librarian(modeladmin, request, queryset):
    queryset.update(user_type='librarian')

@admin.action(description='Change user to student')
def change_user_to_librarian(modeladmin, request, queryset):
    queryset.update(user_type='student')