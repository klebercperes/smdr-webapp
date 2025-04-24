from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Article, ArticleImage
from django.utils import timezone
from django.core.files import File
from io import BytesIO
from PIL import Image
import os

class Command(BaseCommand):
    help = 'Creates dummy articles with images for testing'

    def handle(self, *args, **kwargs):
        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )

        # Sample article data
        articles_data = [
            {
                'title': 'The Future of Artificial Intelligence',
                'summary': 'Exploring the latest developments in AI and machine learning.',
                'content': 'Artificial Intelligence is transforming industries worldwide...',
                'tags': ['AI', 'Technology', 'Future']
            },
            {
                'title': 'Sustainable Living Tips',
                'summary': 'Practical ways to reduce your environmental footprint.',
                'content': 'Living sustainably is more important than ever...',
                'tags': ['Sustainability', 'Environment', 'Lifestyle']
            },
            {
                'title': 'Digital Marketing Trends 2024',
                'summary': 'Key trends shaping the digital marketing landscape.',
                'content': 'The digital marketing world is constantly evolving...',
                'tags': ['Marketing', 'Digital', 'Business']
            },
            {
                'title': 'Healthy Eating Habits',
                'summary': 'Simple changes for a healthier lifestyle.',
                'content': 'Good nutrition is the foundation of a healthy life...',
                'tags': ['Health', 'Nutrition', 'Wellness']
            },
            {
                'title': 'Remote Work Best Practices',
                'summary': 'Tips for staying productive while working from home.',
                'content': 'Remote work has become the new normal...',
                'tags': ['Work', 'Productivity', 'Remote']
            },
            {
                'title': 'Financial Planning Basics',
                'summary': 'Essential steps for securing your financial future.',
                'content': 'Financial planning is crucial for long-term stability...',
                'tags': ['Finance', 'Planning', 'Money']
            }
        ]

        # Create dummy images
        def create_dummy_image():
            img = Image.new('RGB', (800, 600), color='red')
            img_io = BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            return img_io

        # Create articles
        for article_data in articles_data:
            article = Article.objects.create(
                title=article_data['title'],
                summary=article_data['summary'],
                content=article_data['content'],
                author=user,
                status='published',
                publish=timezone.now()
            )
            
            # Add tags
            for tag in article_data['tags']:
                article.tags.add(tag)
            
            # Create and add images
            for i in range(3):  # Create 3 images per article
                img_io = create_dummy_image()
                article_image = ArticleImage.objects.create(
                    article=article,
                    caption=f'Image {i+1} for {article.title}',
                    order=i
                )
                article_image.image.save(
                    f'dummy_image_{article.id}_{i}.jpg',
                    File(img_io),
                    save=True
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created article: {article.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully created dummy articles')) 