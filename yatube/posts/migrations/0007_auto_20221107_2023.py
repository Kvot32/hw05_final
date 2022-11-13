# Generated by Django 2.2.16 on 2022-11-07 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0006_auto_20220928_1214"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="group",
            options={
                "ordering": ("title",),
                "verbose_name": "Жанр",
                "verbose_name_plural": "Жанры",
            },
        ),
        migrations.AlterModelOptions(
            name="post",
            options={
                "ordering": ("-pub_date",),
                "verbose_name": "Пост",
                "verbose_name_plural": "Посты",
            },
        ),
        migrations.AlterField(
            model_name="post",
            name="text",
            field=models.TextField(verbose_name="Текст поста"),
        ),
    ]