from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    profile_picture = models.ImageField(
        _('Profile Picture'),
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Company Information
    company_name = models.CharField(_('Company Name'), max_length=200, blank=True)
    company_logo = models.ImageField(
        _('Company Logo'),
        upload_to='company_logos/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class IpecsReport(models.Model):
    file_name = models.CharField(_('File Name'), max_length=255)
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)
    processed_at = models.DateTimeField(_('Processed At'), null=True, blank=True)
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    file = models.FileField(_('Report File'), upload_to='smdr_reports/')
    total_records = models.IntegerField(_('Total Records'), default=0)
    processed_records = models.IntegerField(_('Processed Records'), default=0)
    error_message = models.TextField(_('Error Message'), blank=True)
    
    class Meta:
        verbose_name = _('Ipecs Report')
        verbose_name_plural = _('Ipecs Reports')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def clean_station_number(self, station_number):
        """Clean station number by removing extra spaces and special characters."""
        if not station_number:
            return ''
        return ''.join(station_number.split()).strip()
    
    def process_file(self):
        """Process the uploaded SMDR report file."""
        import gzip
        import pandas as pd
        from io import StringIO
        
        try:
            self.status = 'processing'
            self.save()
            
            # Read the gzipped file
            with gzip.open(self.file.path, 'rt') as f:
                content = f.read()
            
            # Parse the SLK file
            df = pd.read_csv(StringIO(content), sep=';')
            
            # Clean station numbers
            if 'Station Number' in df.columns:
                df['Station Number'] = df['Station Number'].apply(self.clean_station_number)
            
            # Update record counts
            self.total_records = len(df)
            self.processed_records = len(df)
            self.status = 'completed'
            self.processed_at = timezone.now()
            self.save()
            
            return df
            
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
            self.save()
            raise
