import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание группы",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст поста",
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def test_forms_show_correct(self):
        """Проверка коректности формы поста."""
        url_filds = {
            reverse("posts:post_create"),
            reverse(
                "posts:post_edit",
                kwargs={
                    "post_id": self.post.id,
                },
            ),
        }
        for reverse_page in url_filds:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context["form"].fields["text"],
                    forms.fields.CharField
                )
                self.assertIsInstance(
                    response.context["form"].fields["group"],
                    forms.fields.ChoiceField
                )
                self.assertIsInstance(
                    response.context["form"].fields["image"],
                    forms.fields.ImageField
                )

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        self.check_post_info(response.context["page_obj"][0])

    def test_groups_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list",
                    kwargs={"slug": self.group.slug})

        )
        self.assertEqual(response.context["group"], self.group)
        self.check_post_info(response.context["page_obj"][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:profile",
                    kwargs={"username": self.user.username}
                    )
        )
        self.assertEqual(response.context["author"], self.user)
        self.check_post_info(response.context["page_obj"][0])

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.id}
                    )
        )
        self.check_post_info(response.context["post"])

    def test_cache_index_page(self):
        """Проверка работы кеша"""
        post = Post.objects.create(text="Пост под кеш", author=self.user)
        content_add = self.authorized_client.get(
            reverse("posts:index")
        ).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse("posts:index")
        ).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.authorized_client.get(
            reverse("posts:index")
        ).content
        self.assertNotEqual(content_add, content_cache_clear)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TaskPagesTests, cls).setUpClass()
        cls.user = User.objects.create_user(
            username="HasNoName"
        )
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group_slug",
            description="Test group description",
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT,
                      ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_image_in_group_list_page(self):
        """Картинка передается на страницу group_list."""
        response = self.guest_client.get(
            reverse("posts:group_list",
                    kwargs={"slug": self.group.slug}
                    ),
        )
        obj = response.context["page_obj"][0]
        self.assertEqual(obj.image, self.post.image)

    def test_image_in_index_and_profile_page(self):
        """Картинка передается на страницу index_and_profile."""
        templates = (
            reverse("posts:index"),
            reverse("posts:profile",
                    kwargs={"username": self.post.author}
                    ),
        )
        for url in templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                obj = response.context["page_obj"][0]
                self.assertEqual(obj.image, self.post.image)

    def test_image_in_post_detail_page(self):
        """Картинка передается на страницу post_detail."""
        response = self.guest_client.get(
            reverse("posts:post_detail",
                    kwargs={"post_id": self.post.id}
                    )
        )
        obj = response.context["post"]
        self.assertEqual(obj.image, self.post.image)

    def test_image_in_page(self):
        """Проверяем что пост с картинкой создается в БД"""
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
                image="posts/small.gif").exists()
        )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_autor = User.objects.create(
            username="post_autor",
        )
        cls.post_follower = User.objects.create(
            username="post_follower",
        )
        cls.post = Post.objects.create(
            text="Подпишись на меня",
            author=cls.post_autor,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.post_follower)
        self.follower_client = Client()
        self.follower_client.force_login(self.post_autor)

    def test_follow_on_user(self):
        """Проверка подписки на пользователя."""
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse("posts:profile_follow",
                    kwargs={"username": self.post_follower}
                    )
        )
        follow = Follow.objects.all().latest("id")
        self.assertEqual(Follow.objects.count(),
                         count_follow + 1
                         )
        self.assertEqual(follow.author_id,
                         self.post_follower.id
                         )
        self.assertEqual(follow.user_id,
                         self.post_autor.id
                         )

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(user=self.post_autor,
                              author=self.post_follower)
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse("posts:profile_unfollow",
                    kwargs={"username": self.post_follower})
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_on_authors(self):
        """Проверка записей у тех кто подписан."""
        post = Post.objects.create(
            author=self.post_autor,
            text="Подпишись на меня"
        )
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_autor
        )
        response = self.author_client.get(
            reverse("posts:follow_index")
        )
        self.assertIn(post,
                      response.context["page_obj"].object_list)

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан."""
        post = Post.objects.create(
            author=self.post_autor,
            text="Подпишись на меня"
        )
        response = self.author_client.get(reverse("posts:follow_index"))
        self.assertNotIn(post,
                         response.context["page_obj"].object_list)
