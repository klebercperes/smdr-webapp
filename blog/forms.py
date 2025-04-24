from django import forms
from ckeditor.widgets import CKEditorWidget
from django.utils.text import slugify
from taggit.forms import TagWidget
from .models import Article, Comment, ArticleImage, ArticleVideo

class TagInputWidget(TagWidget):
    def format_value(self, value):
        if value is not None and not isinstance(value, str):
            value = ', '.join([tag.name for tag in value])
        return value

class ArticleForm(forms.ModelForm):
    tags_suggestions = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        initial='Technology, Health, Healthcare, Innovation, Science, AI'
    )

    class Meta:
        model = Article
        fields = ['title', 'summary', 'content', 'status', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter article title'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Write a brief summary of your article'
            }),
            'content': CKEditorWidget(config_name='advanced', attrs={
                'class': 'w-full',
                'config': {
                    'allowedContent': True,
                    'removeFormatAttributes': '',
                    'height': '400px',
                    'toolbar': [
                        {'name': 'styles', 'items': ['Format', 'Font', 'FontSize']},
                        {'name': 'basicstyles',
                         'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
                        {'name': 'paragraph',
                         'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                                  'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
                        {'name': 'links', 'items': ['Link', 'Unlink']},
                        {'name': 'insert',
                         'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar']},
                        {'name': 'colors', 'items': ['TextColor', 'BGColor']},
                        {'name': 'tools', 'items': ['Maximize', 'ShowBlocks', 'Source']},
                    ],
                    'extraPlugins': 'autogrow,divarea,colorbutton,colordialog,font',
                    'autoGrow_minHeight': 400,
                    'autoGrow_maxHeight': 800,
                    'removeDialogTabs': '',
                    'format_tags': 'p;h1;h2;h3;h4;h5;h6;pre;div',
                    'contentsCss': [
                        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 16px; line-height: 1.6; }',
                        'h1 { font-size: 2em; margin-bottom: 0.5em; font-weight: bold; }',
                        'h2 { font-size: 1.5em; margin-bottom: 0.5em; font-weight: bold; }',
                        'h3 { font-size: 1.17em; margin-bottom: 0.5em; font-weight: bold; }',
                        'h4 { font-size: 1em; margin-bottom: 0.5em; font-weight: bold; }',
                        'p { margin-bottom: 1em; }',
                        'ul, ol { margin-bottom: 1em; padding-left: 2em; }',
                        'blockquote { margin: 1em 0; padding: 0.5em 1em; border-left: 3px solid #e5e7eb; background: #f3f4f6; }',
                    ],
                }
            }),
            'tags': TagInputWidget(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter tags separated by commas'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            })
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        # Always update slug when title changes, for both new and existing articles
        if not self.instance.pk or (self.instance.title != title):
            self.instance.slug = slugify(title)
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            # Allow all HTML content
            return content
        return content

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            })
        }

class ArticleImageForm(forms.ModelForm):
    class Meta:
        model = ArticleImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'caption': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        }

class ArticleVideoForm(forms.ModelForm):
    class Meta:
        model = ArticleVideo
        fields = ['youtube_url', 'video_file', 'caption', 'order']
        widgets = {
            'youtube_url': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'caption': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
            'order': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg'}),
        } 