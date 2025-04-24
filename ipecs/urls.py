from django.urls import path
from . import views

app_name = 'ipecs'

urlpatterns = [
    path('reports/', views.IpecsReportListView.as_view(), name='report-list'),
    path('reports/create/', views.IpecsReportCreateView.as_view(), name='report-create'),
    path('reports/<int:pk>/', views.report_detail, name='report-detail'),
    path('reports/<int:pk>/delete/', views.IpecsReportDeleteView.as_view(), name='report-delete'),
] 