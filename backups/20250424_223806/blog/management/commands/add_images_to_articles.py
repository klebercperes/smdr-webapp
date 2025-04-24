from django.core.management.base import BaseCommand
from blog.models import Article, ArticleImage
from django.core.files import File
from PIL import Image
import os
from io import BytesIO

class Command(BaseCommand):
    help = 'Adds images to existing articles'

    def handle(self, *args, **options):
        # Sample images data
        sample_images = [
            {
                'caption': 'Technology in action',
                'description': 'Modern technology at work'
            },
            {
                'caption': 'Innovation showcase',
                'description': 'Latest innovations in the field'
            },
            {
                'caption': 'Expert insights',
                'description': 'Professional analysis and insights'
            }
        ]

        # Get all published articles
        articles = Article.objects.filter(status='published')

        for article in articles:
            self.stdout.write(f'Processing article: {article.title}')
            
            # Create 3 images for each article
            for i, img_data in enumerate(sample_images):
                # Create a dummy image
                img = Image.new('RGB', (800, 600), color=(73, 109, 137))
                
                # Add some text to make it unique
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                font = ImageFont.load_default()
                draw.text((10, 10), f"{article.title[:20]} - Image {i+1}", fill=(255, 255, 255))
                
                # Save to BytesIO
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                
                # Create ArticleImage instance
                article_image = ArticleImage(
                    article=article,
                    caption=img_data['caption'],
                    description=img_data['description'],
                    order=i
                )
                
                # Save the image
                article_image.image.save(
                    f'{article.slug}_image_{i+1}.jpg',
                    File(img_io),
                    save=True
                )
                
                self.stdout.write(f'  Added image: {img_data["caption"]}')

        self.stdout.write(self.style.SUCCESS('Successfully added images to all articles')) 