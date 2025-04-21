from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.validators import FileExtensionValidator

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'profile_picture', 'company_name', 'company_logo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError('Profile picture size should not exceed 2MB.')
            if not picture.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload an image file.')
        return picture

    def clean_company_logo(self):
        logo = self.cleaned_data.get('company_logo')
        if logo:
            if logo.size > 2 * 1024 * 1024:  # 2MB limit
                raise forms.ValidationError('Company logo size should not exceed 2MB.')
            if not logo.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload an image file.')
        return logo

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone_number 