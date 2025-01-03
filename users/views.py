from django.shortcuts import render, redirect
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import StudentProfile,LibrarianProfile,AdminProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
# Create your views here.

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = form.cleaned_data['user_type']  # Set user_type before saving
                user.save()
                
                # Create appropriate profile based on user type
                if user.user_type == 'student':
                    StudentProfile.objects.create(user=user)
                elif user.user_type == 'librarian':
                    LibrarianProfile.objects.create(user=user)
                elif user.user_type == 'admin' or user.is_superuser:
                    AdminProfile.objects.create(user=user)
                messages.success(request, "Your account has been created")
                return redirect('login')
            except ValidationError as e:
                messages.error(request, str(e))
                user.delete()  # Delete the user if profile creation fails
                return redirect('sign_up')
    else:
        form=RegisterForm()
    
    return render(request, 'users/sign_up.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    
    # Get or create profile instance
    try:
        if user.is_superuser:
            profile_instance = AdminProfile.objects.get_or_create(user=user)[0]
            user.user_type = 'admin'
            user.save()
        else:
            if user.user_type == 'admin':
                profile_instance = user.adminprofile
            elif user.user_type == 'librarian':
                profile_instance = user.librarianprofile
            elif user.user_type == 'student':
                profile_instance = user.studentprofile
    except:
        messages.error(request, f'Profile not found for {user.user_type}')
        return redirect('home')

    if request.method == 'POST':
        # Handle form submission
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(
            data=request.POST,
            files=request.FILES,
            instance=profile_instance,
            user=user
        )
    else:
        # Display current data
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile_instance, user=user)

    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'Your profile has been updated!')
        return redirect('profile')

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile.html', context)

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')