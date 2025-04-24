from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings
import os
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from simple_history.models import HistoricalRecords

def validate_file_size(value):
    if value.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(f'File size cannot exceed {settings.MAX_UPLOAD_SIZE/1048576:.1f}MB')

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_articles')
    summary = models.TextField(max_length=500)
    content = RichTextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    tags = TaggableManager()
    history = HistoricalRecords()
    
    class Meta:
        ordering = ('-publish',)
        indexes = [
            models.Index(fields=['-publish']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:article_detail', args=[
            self.publish.year,
            self.publish.month,
            self.publish.day,
            self.slug
        ])

class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog/images/', validators=[validate_file_size])
    thumbnail = ImageSpecField(source='image',
                             processors=[ResizeToFill(300, 200)],
                             format='JPEG',
                             options={'quality': 60})
    caption = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.article.title}"

    def safe_delete_file(self, file_field):
        """Safely delete a file field"""
        if not file_field:
            return
        
        try:
            # Get the file name and check if it exists
            file_name = file_field.name
            if default_storage.exists(file_name):
                default_storage.delete(file_name)
        except Exception:
            # Ignore any errors during file deletion
            pass

    def safe_delete_thumbnail(self):
        """Safely delete the thumbnail file"""
        try:
            if hasattr(self.thumbnail, 'path'):
                thumbnail_path = self.thumbnail.path
                if os.path.isfile(thumbnail_path):
                    os.remove(thumbnail_path)
        except Exception:
            # Ignore any errors during thumbnail deletion
            pass

@receiver(pre_delete, sender=ArticleImage)
def delete_article_image_files(sender, instance, **kwargs):
    """Delete image files when ArticleImage instance is deleted"""
    instance.safe_delete_file(instance.image)
    instance.safe_delete_thumbnail()

@receiver(pre_delete, sender=Article)
def delete_article_files(sender, instance, **kwargs):
    """Delete all associated files when an Article is deleted"""
    for image in instance.images.all():
        image.safe_delete_file(image.image)
        image.safe_delete_thumbnail()
    
    # Handle video files if they exist
    for video in instance.videos.all():
        if video.video_file:
            video.safe_delete_file(video.video_file)

class ArticleVideo(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='videos')
    youtube_url = models.URLField(blank=True)
    video_file = models.FileField(upload_to='blog/videos/', blank=True)
    caption = models.CharField(max_length=250, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Video for {self.article.title}"

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'

class ReadLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_later')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='read_later_by')
    added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'article')
        ordering = ['-added']
    
    def __str__(self):
        return f"{self.user.username} wants to read {self.article.title} later"
