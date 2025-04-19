from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

# Create your views here.

def home(request):
    return render(request, 'home.html')

def test_email(request):
    try:
        send_mail(
            'Test Email',
            'This is a test email from your Django application.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return HttpResponse('Email sent successfully!')
    except Exception as e:
        return HttpResponse(f'Failed to send email: {str(e)}')
