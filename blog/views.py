from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.forms import inlineformset_factory
from .models import Article, Comment, ReadLater, ArticleImage
from .forms import ArticleForm, CommentForm, ArticleImageForm
from django.utils.text import slugify

ArticleImageFormSet = inlineformset_factory(
    Article, ArticleImage, form=ArticleImageForm,
    extra=3, can_delete=True, can_order=True
)

class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'article_list'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = Article.objects.filter(status='published').exclude(slug='')
        search_query = self.request.GET.get('search')
        tag_slug = self.request.GET.get('tag')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(summary__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
            
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
            
        return queryset.order_by('-publish')

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['is_saved'] = ReadLater.objects.filter(
                user=self.request.user,
                article=self.object
            ).exists()
        return context

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ArticleImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = ArticleImageFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            form.instance.author = self.request.user
            if not form.instance.slug:
                form.instance.slug = slugify(form.instance.title)
            self.object = form.save()
            image_formset.instance = self.object
            image_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
            
    def get_success_url(self):
        return self.object.get_absolute_url()

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ArticleImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['image_formset'] = ArticleImageFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        try:
            context = self.get_context_data()
            image_formset = context['image_formset']
            
            if form.is_valid() and image_formset.is_valid():
                # Save the form first
                self.object = form.save(commit=False)
                # Update the slug if title changed
                if 'title' in form.changed_data:
                    self.object.slug = slugify(self.object.title)
                self.object.save()
                form.save_m2m()  # Save tags
                
                # Save the image formset
                image_formset.instance = self.object
                image_formset.save()
                
                messages.success(self.request, 'Article updated successfully.')
                return super().form_valid(form)
            else:
                return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error updating article: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('blog:article_list')
    
    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.article = get_object_or_404(Article, pk=self.kwargs['pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.article.get_absolute_url()

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
    
    def get_success_url(self):
        return self.object.article.get_absolute_url()

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
    
    def get_success_url(self):
        return self.object.article.get_absolute_url()

class ReadLaterListView(LoginRequiredMixin, ListView):
    model = ReadLater
    template_name = 'blog/read_later_list.html'
    context_object_name = 'saved_articles'
    
    def get_queryset(self):
        return ReadLater.objects.filter(user=self.request.user)

def toggle_read_later(request, pk):
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    article = get_object_or_404(Article, pk=pk)
    read_later, created = ReadLater.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    if not created:
        read_later.delete()
        messages.success(request, 'Article removed from Read Later list.')
    else:
        messages.success(request, 'Article added to Read Later list.')
    
    return redirect(article.get_absolute_url())
