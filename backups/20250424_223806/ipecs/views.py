from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import IpecsReport
from .forms import IpecsReportUploadForm
import json
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class IpecsReportListView(LoginRequiredMixin, ListView):
    model = IpecsReport
    template_name = 'ipecs/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10

    def get_queryset(self):
        return IpecsReport.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = IpecsReportUploadForm()
        context['total_reports'] = self.get_queryset().count()
        context['completed_reports'] = self.get_queryset().filter(status='completed').count()
        context['pending_reports'] = self.get_queryset().filter(status='pending').count()
        context['active_tab'] = 'reports'
        return context

    def post(self, request, *args, **kwargs):
        form = IpecsReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()
            messages.success(request, 'Report uploaded successfully.')
            return redirect('ipecs:report-detail', pk=report.pk)
        messages.error(request, 'Error uploading report.')
        return self.get(request, *args, **kwargs)

class IpecsReportCreateView(LoginRequiredMixin, CreateView):
    model = IpecsReport
    template_name = 'ipecs/report_create.html'
    fields = ['file']
    success_url = reverse_lazy('ipecs:report-list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the current user
        form.instance.file_name = form.instance.file.name
        response = super().form_valid(form)
        try:
            form.instance.process_file()
            messages.success(self.request, 'Report processed successfully!')
        except Exception as e:
            messages.error(self.request, f'Error processing report: {str(e)}')
        return response

@login_required
def report_detail(request, pk):
    report = get_object_or_404(IpecsReport, pk=pk, user=request.user)
    context = {
        'report': report,
        'active_tab': 'reports'
    }

    try:
        # Get the raw data from the report
        raw_data = report.get_data()
        logger.info(f"Raw data type: {type(raw_data)}")
        
        if raw_data:
            # If the data is a string (JSON), try to parse it
            if isinstance(raw_data, str):
                try:
                    raw_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON data")
                    raise ValueError("Invalid data format")

            # Handle the new data structure
            if isinstance(raw_data, dict) and 'headers' in raw_data and 'data' in raw_data:
                headers = raw_data['headers']
                table_data = raw_data['data']
            else:
                # Fallback for old data format
                headers = raw_data[0] if isinstance(raw_data, list) and raw_data else []
                table_data = raw_data[1:] if isinstance(raw_data, list) and len(raw_data) > 1 else []

            logger.info(f"Headers: {headers}")
            logger.info(f"Number of data rows: {len(table_data)}")
            
            # Set up pagination
            paginator = Paginator(table_data, 25)  # 25 rows per page
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'headers': headers,
                'data': page_obj,
                'show_pagination': paginator.num_pages > 1,
                'page_obj': page_obj,
                'paginator': paginator,
            })
            
    except Exception as e:
        logger.exception("Error processing report data")
        context['error_message'] = f"Error processing report: {str(e)}"
        context['error_type'] = type(e).__name__

    return render(request, 'ipecs/report_detail.html', context)

class IpecsReportDeleteView(LoginRequiredMixin, DeleteView):
    model = IpecsReport
    success_url = reverse_lazy('ipecs:report-list')
    template_name = 'ipecs/report_confirm_delete.html'

    def get_queryset(self):
        # Ensure users can only delete their own reports
        return IpecsReport.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        report = self.get_object()
        messages.success(request, f'Report "{report.file_name}" was successfully deleted.')
        return super().delete(request, *args, **kwargs)
