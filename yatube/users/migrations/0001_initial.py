# Generated by Django 2.2.9 on 2022-10-08 13:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("isbn", models.CharField(max_length=100)),
                (
                    "pages",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
            ],
        ),
    ]