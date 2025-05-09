# Generated by Django 5.2 on 2025-04-21 04:59

from django.db import migrations
from django.utils.text import slugify

def set_article_slugs(apps, schema_editor):
    Article = apps.get_model('blog', 'Article')
    for article in Article.objects.filter(slug=''):
        article.slug = slugify(article.title)
        article.save()

class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_article_slugs),
    ]
