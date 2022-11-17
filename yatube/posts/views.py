from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic import View

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def _get_page_context(request, queryset):
    paginator = Paginator(queryset, settings.POST_NUMBER)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix="index_page")
def index(request):
    posts = Post.objects.select_related("group")
    post_list = Post.objects.select_related("author").all()
    page_obj = _get_page_context(request=request, queryset=posts)
    context = {"page_obj": page_obj, "post_list": post_list}
    return render(request, "posts/index.html", context)


class GroupList(View):
    def get(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        posts = group.posts.select_related("group")
        page_obj = _get_page_context(request=request, queryset=posts)
        context = {"group": group, "page_obj": page_obj}
        return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    page_obj = _get_page_context(request=request, queryset=posts)
    followers = Follow.objects.filter(author__username=username).count()
    context = {
        "author": author,
        "page_obj": page_obj,
        "followers": followers
    }
    if request.user.is_authenticated:
        following = author.following.exists()
        context.update(
            {
                "following": following,
                "user": request.user,
            }
        )
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    template = "posts/post_detail.html"
    context = {
        "post": post,
        "requser": request.user,
        "form": form,
        "comments": comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    files = request.FILES or None
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect("posts:profile", create_post.author)
    template = "posts/create_post.html"
    context = {"form": form, "is_edit": False, "filse": files}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    template = "posts/create_post.html"
    context = {"form": form, "is_edit": True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    list_posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related("author", "group")
    page_obj = _get_page_context(request, list_posts)
    context = {"page_obj": page_obj}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
        not User.objects.filter(
            username=author,
            following__user=request.user,
        ).exists()
        and author != request.user
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    old = Follow.objects.filter(
        user=request.user,
        author=author
    )
    if old.exists():
        old.delete()
    return redirect("posts:profile", username=author)
