from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import UserProfileForm
from blog.models import Article
from django.db.models import Count
from ipecs.models import IpecsReport
from django.contrib.auth.models import User

def home(request):
    latest_article = Article.objects.filter(status='published').order_by('-publish').first()
    return render(request, 'home.html', {
        'latest_article': latest_article
    })

def about(request):
    return render(request, 'smdr/about.html')

@login_required
def user_details(request, username=None, tab=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile = user.profile
    active_tab = tab or request.GET.get('tab', 'profile')
    
    context = {
        'user': user,
        'profile': profile,
        'active_tab': active_tab,
    }
    
    if active_tab == 'reports':
        # Get reports data
        reports = IpecsReport.objects.filter(user=user).order_by('-created_at')
        total_reports = reports.count()
        completed_reports = reports.filter(status='completed').count()
        pending_reports = total_reports - completed_reports
        
        context.update({
            'reports': reports,
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'pending_reports': pending_reports,
            'show_pagination': len(reports) > 10,
        })
    
    return render(request, 'smdr/user_details.html', context)

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
                return redirect('smdr:account_profile')
            except Exception as e:
                messages.error(request, f'Error saving profile: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'smdr/profile.html', {
        'form': form,
        'profile': request.user.profile,
        'active_tab': 'profile'
    })
