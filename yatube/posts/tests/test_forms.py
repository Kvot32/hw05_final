from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в БД."""
        posts_count = Post.objects.count()
        form_data = {"text": "Тестовый пост"}
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile",
                    kwargs={
                        "username": PostFormTests.user.username
                    }
                    ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        """Валидная форма изменяет запись БД."""
        self.post = Post.objects.create(
            author=PostFormTests.user,
            text="Тестовый пост",
        )
        posts_count = Post.objects.count()
        form_data = {"text": "Тестовый пост", "author": PostFormTests.user}
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )

        self.assertEqual(Post.objects.count(), posts_count)

        self.assertEqual(self.post.text, form_data["text"])
        self.assertEqual(self.post.author, form_data["author"])

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_post(self):
        """Комментировать посты может только авторизованный пользователь."""
        comment_count = Comment.objects.count()
        self.post = Post.objects.create(
            author=PostFormTests.user,
            text="Тестовый пост",
            group=PostFormTests.group,
        )
        comment_data = {
            "text": "Тестовый комментарий",
        }
        self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=comment_data,
            follow=True,
        )
        new_comment = Comment.objects.get(text=comment_data["text"])
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(new_comment.text, comment_data["text"])

    def test_comment_client_post(self):
        """Неавторизованный пользователь не может оставить комментарий."""
        comment_count = Comment.objects.count()
        self.post = Post.objects.create(
            author=PostFormTests.user,
            text="Тестовый пост",
            group=PostFormTests.group,
        )
        comment_data = {
            "text": "Тестовый комментарий",
        }
        self.guest_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=comment_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count)
