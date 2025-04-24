import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from blog.models import Article, ArticleImage
from django.contrib.auth import get_user_model
from faker import Faker
import random
from PIL import Image
from io import BytesIO

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Downloads real images and generates realistic content for articles'

    def handle(self, *args, **kwargs):
        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()

        # Sample article data with realistic topics
        articles_data = [
            {
                'title': 'The Future of Artificial Intelligence in Healthcare',
                'summary': 'Exploring how AI is revolutionizing healthcare delivery and patient care.',
                'tags': ['Technology', 'Health', 'Science', 'AI', 'Healthcare', 'Innovation']
            },
            {
                'title': 'Sustainable Business Practices for Modern Companies',
                'summary': 'How businesses can implement eco-friendly practices while maintaining profitability.',
                'tags': ['Business', 'Lifestyle', 'Finance', 'Sustainability', 'Environment', 'Corporate']
            },
            {
                'title': 'Digital Marketing Trends to Watch in 2024',
                'summary': 'The latest strategies and technologies shaping the future of digital marketing.',
                'tags': ['Business', 'Technology', 'Education', 'Marketing', 'Digital', 'Trends']
            },
            {
                'title': 'Healthy Eating Habits for Busy Professionals',
                'summary': 'Practical tips for maintaining a balanced diet despite a hectic schedule.',
                'tags': ['Health', 'Lifestyle', 'Food', 'Nutrition', 'Wellness', 'Professional']
            },
            {
                'title': 'Financial Planning Basics for Young Adults',
                'summary': 'Essential financial management skills everyone should learn early in life.',
                'tags': ['Finance', 'Education', 'Lifestyle', 'Money', 'Planning', 'Young-Adults']
            },
            {
                'title': 'Remote Work Best Practices and Productivity Tips',
                'summary': 'How to maintain efficiency and work-life balance while working from home.',
                'tags': ['Business', 'Lifestyle', 'Technology', 'Remote-Work', 'Productivity', 'Work-Life']
            }
        ]

        # Download and process images
        for article_data in articles_data:
            # Create the article
            article = Article.objects.create(
                title=article_data['title'],
                slug=article_data['title'].lower().replace(' ', '-'),
                author=user,
                summary=article_data['summary'],
                content=self.generate_realistic_content(),
                status='published',
                publish=timezone.now()
            )

            # Add tags
            article.tags.add(*article_data['tags'])

            # Download and add 3 images for each article
            for i in range(3):
                try:
                    # Download image from Unsplash
                    response = requests.get(f'https://source.unsplash.com/800x600/?{article_data["tags"][0].lower()}')
                    if response.status_code == 200:
                        # Create a unique filename
                        filename = f'{article.slug}_image_{i+1}.jpg'
                        
                        # Save the image
                        image = ArticleImage.objects.create(
                            article=article,
                            image=ContentFile(response.content, name=filename),
                            caption=f'Image {i+1} for {article.title}',
                            order=i,
                            description=f'This image illustrates the concept of {article_data["tags"][0].lower()} in relation to {article.title.lower()}'
                        )
                        
                        # Process the image to create thumbnail
                        img = Image.open(BytesIO(response.content))
                        img.thumbnail((300, 300))
                        thumb_io = BytesIO()
                        img.save(thumb_io, format='JPEG')
                        image.thumbnail.save(
                            f'thumb_{filename}',
                            ContentFile(thumb_io.getvalue()),
                            save=False
                        )
                        image.save()
                        
                        self.stdout.write(self.style.SUCCESS(f'Successfully downloaded and processed image {i+1} for {article.title}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing image {i+1} for {article.title}: {str(e)}'))

            self.stdout.write(self.style.SUCCESS(f'Successfully created article: {article.title}'))

    def generate_realistic_content(self):
        # Generate a realistic article content with multiple paragraphs
        paragraphs = []
        for _ in range(5):  # Generate 5 paragraphs
            paragraph = fake.paragraph(nb_sentences=6)
            paragraphs.append(f'<p>{paragraph}</p>')
        
        # Add some headings
        content = f'''
        <h2>Introduction</h2>
        {paragraphs[0]}
        
        <h2>Key Concepts</h2>
        {paragraphs[1]}
        
        <h2>Implementation Strategies</h2>
        {paragraphs[2]}
        
        <h2>Case Studies</h2>
        {paragraphs[3]}
        
        <h2>Conclusion</h2>
        {paragraphs[4]}
        
        <h3>References</h3>
        <ul>
            <li>{fake.uri()}</li>
            <li>{fake.uri()}</li>
            <li>{fake.uri()}</li>
        </ul>
        '''
        return content 