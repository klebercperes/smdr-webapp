from django.contrib import admin
from django.utils.html import format_html
from .models import Article, ArticleImage, ArticleVideo, Comment, ReadLater

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('image', 'caption', 'order')

class ArticleVideoInline(admin.TabularInline):
    model = ArticleVideo
    extra = 1
    fields = ('youtube_url', 'video_file', 'caption', 'order')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'status', 'display_tags')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', '-publish')
    inlines = [ArticleImageInline, ArticleVideoInline]
    
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Tags'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('content', 'author__username', 'article__title')
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(active=True)
    approve_comments.short_description = 'Approve selected comments'

@admin.register(ReadLater)
class ReadLaterAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'added')
    list_filter = ('added',)
    search_fields = ('user__username', 'article__title')
