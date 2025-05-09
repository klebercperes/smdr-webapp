# Generated by Django 5.2 on 2025-04-22 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("smdr", "0002_setup_site"),
    ]

    operations = [
        migrations.CreateModel(
            name="IpecsReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file_name",
                    models.CharField(max_length=255, verbose_name="File Name"),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At"),
                ),
                (
                    "processed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Processed At"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Status",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="smdr_reports/", verbose_name="Report File"
                    ),
                ),
                (
                    "total_records",
                    models.IntegerField(default=0, verbose_name="Total Records"),
                ),
                (
                    "processed_records",
                    models.IntegerField(default=0, verbose_name="Processed Records"),
                ),
                (
                    "error_message",
                    models.TextField(blank=True, verbose_name="Error Message"),
                ),
            ],
            options={
                "verbose_name": "Ipecs Report",
                "verbose_name_plural": "Ipecs Reports",
                "ordering": ["-uploaded_at"],
            },
        ),
    ]
