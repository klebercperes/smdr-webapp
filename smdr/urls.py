from django.urls import path
from . import views
from django.conf import settings

app_name = 'smdr'

if settings.DEBUG:
    print("SMDR URL patterns:")
    print("1. Home URL: /")
    print("2. Profile URL: /profile/")

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile_view, name='profile'),
]
