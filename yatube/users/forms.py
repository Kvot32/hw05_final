from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Book

User = get_user_model()


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("name", "isbn", "pages")


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")
