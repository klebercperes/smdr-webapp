from django.db import migrations
from django.contrib.sites.models import Site

def setup_site(apps, schema_editor):
    Site.objects.get_or_create(
        id=2,
        defaults={
            'domain': 'peres.au',
            'name': 'peres.au'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('smdr', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(setup_site),
    ] 