from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import UserProfileForm

def home(request):
    return render(request, 'home.html')

@login_required
def user_details(request):
    return render(request, 'smdr/user_details.html', {
        'profile': request.user.profile
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            try:
                # Handle file uploads
                if 'profile_picture' in request.FILES:
                    profile_picture = request.FILES['profile_picture']
                    fs = FileSystemStorage()
                    filename = fs.save(f'profile_pictures/{request.user.username}_{profile_picture.name}', profile_picture)
                    form.instance.profile_picture = filename

                if 'company_logo' in request.FILES:
                    company_logo = request.FILES['company_logo']
                    fs = FileSystemStorage()
                    filename = fs.save(f'company_logos/{request.user.username}_{company_logo.name}', company_logo)
                    form.instance.company_logo = filename

                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('account_profile')
            except Exception as e:
                messages.error(request, f'Error saving profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'smdr/profile.html', {
        'form': form,
        'profile': request.user.profile
    })
