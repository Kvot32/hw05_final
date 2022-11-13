from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=200)
    isbn = models.CharField(max_length=100)
    pages = models.IntegerField(validators=[MinValueValidator(1)])
