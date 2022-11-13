from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import BookForm, CreationForm


class BookView(CreateView):
    form_class = BookForm
    template_name = "library/new_book.html"
    success_url = "thankyou/"


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


def only_user_view(request):
    if not request.user.is_authenticated:
        return redirect("/auth/login/")
