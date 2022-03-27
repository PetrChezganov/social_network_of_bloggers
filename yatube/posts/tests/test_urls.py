from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestName')
        cls.not_author = User.objects.create_user(username='NotAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.url_template_status = {
            '/': ('posts/index.html', HTTPStatus.OK),
            f'/group/{cls.group.slug}/': (
                'posts/group_list.html', HTTPStatus.OK
            ),
            f'/profile/{cls.author}/': (
                'posts/profile.html', HTTPStatus.OK
            ),
            f'/posts/{cls.post.id}/': (
                'posts/post_detail.html', HTTPStatus.OK
            ),
            f'/posts/{cls.post.id}/comment/': (
                None, HTTPStatus.FOUND
            ),
            '/create/': ('posts/create_post.html', HTTPStatus.FOUND),
            f'/posts/{cls.post.id}/edit/': (
                'posts/create_post.html', HTTPStatus.FOUND
            ),
            '/follow/': ('posts/follow.html', HTTPStatus.FOUND),
            f'/profile/{cls.not_author}/follow/': (
                None, HTTPStatus.FOUND
            ),
            f'/profile/{cls.not_author}/unfollow/': (
                None, HTTPStatus.FOUND
            ),
            f'/profile/{cls.author}/avatar/': (
                'posts/avatar.html', HTTPStatus.FOUND
            ),
            '/unexisting_page/': ('core/404.html', HTTPStatus.NOT_FOUND),
        }
        cls.url_status_for_author = {
            f'/posts/{cls.post.id}/comment/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/delete/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.OK,
            f'/profile/{cls.not_author}/follow/': HTTPStatus.FOUND,
            f'/profile/{cls.not_author}/unfollow/': HTTPStatus.FOUND,
            f'/profile/{cls.author}/avatar/': HTTPStatus.OK,
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.not_author)

    def test_urls_exists_at_desired_location(self):
        """Проверяем общедоступные страницы"""
        for url in self.url_template_status:
            _, status = self.url_template_status[url]
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_exists_at_desired_location_authorized(self):
        """Проверяем доступность страниц для авторизованного автора поста"""
        for url, status in self.url_status_for_author.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_url_redirect_anonymous_on_admin_login(self):
        """Проверяем редиректы для неавторизованного пользователя"""
        url_redirect = {
            f'/posts/{self.post.id}/comment/': (
                f'/auth/login/?next=/posts/{self.post.id}/comment/'
            ),
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': (
                f'/auth/login/?next=/posts/{self.post.id}/edit/'
            ),
            f'/posts/{self.post.id}/delete/': (
                f'/auth/login/?next=/posts/{self.post.id}/delete/'
            ),
            '/follow/': '/auth/login/?next=/follow/',
        }
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_post_url_redirect_not_author_on_post_detail(self):
        """Проверяем редиректы для авторизованного пользователя не автора
        поста"""
        url_redirect = {
            f'/posts/{self.post.id}/comment/': f'/posts/{self.post.id}/',
            f'/posts/{self.post.id}/edit/': f'/posts/{self.post.id}/',
            f'/posts/{self.post.id}/delete/': f'/posts/{self.post.id}/',
            f'/profile/{self.author}/follow/':
                f'/profile/{self.author}/',
            f'/profile/{self.author}/unfollow/':
                f'/profile/{self.author}/',
            f'/profile/{self.author}/avatar/':
                f'/profile/{self.author}/',
        }
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.not_author_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_post_url_redirect_author(self):
        """Проверяем редиректы для авторизованного автора поста"""
        url_redirect = {
            f'/posts/{self.post.id}/comment/': f'/posts/{self.post.id}/',
            f'/posts/{self.post.id}/delete/': f'/profile/{self.author}/',
            f'/profile/{self.author}/follow/':
                f'/profile/{self.author}/',
            f'/profile/{self.author}/unfollow/':
                f'/profile/{self.author}/',
        }
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.author_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        for url in self.url_template_status:
            template, _ = self.url_template_status[url]
            with self.subTest(url=url):
                if url not in (f'/posts/{self.post.id}/comment/',
                               f'/profile/{self.not_author}/follow/',
                               f'/profile/{self.not_author}/unfollow/'
                               ):
                    response = self.author_client.get(url)
                    self.assertTemplateUsed(response, template)
