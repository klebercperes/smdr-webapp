from django.contrib import admin
from .models import IpecsReport

@admin.register(IpecsReport)
class IpecsReportAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('file_name',)
    readonly_fields = ('created_at',)
