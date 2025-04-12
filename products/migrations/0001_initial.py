# Generated by Django 5.1.7 on 2025-04-03 15:01

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
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
                ("productname", models.CharField(max_length=100)),
                ("slug", models.SlugField(blank=True, null=True)),
                ("productimage", models.ImageField(upload_to="")),
                ("packtitle", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("originalprice", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "discountPercentage",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        help_text="Discount percentage (0-100)",
                        max_digits=5,
                    ),
                ),
                (
                    "discountPrice",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Calculated discounted price",
                        max_digits=10,
                        null=True,
                    ),
                ),
                ("stock", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
    ]
