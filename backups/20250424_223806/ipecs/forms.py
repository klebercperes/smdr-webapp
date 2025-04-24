from django import forms
from .models import IpecsReport

class IpecsReportUploadForm(forms.ModelForm):
    class Meta:
        model = IpecsReport
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': '.slk,.csv'
            })
        } 