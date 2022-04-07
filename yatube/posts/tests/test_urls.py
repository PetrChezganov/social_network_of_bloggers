from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

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
        cls.URL_POST_ID = f'/posts/{cls.post.id}/'
        cls.URL_PROFILE_AUTHOR = f'/profile/{cls.author}/'
        cls.REDIRECT_AUTH_LOGIN = '/auth/login/?next='
        cls.url_template_status = {
            '/': ('posts/index.html', HTTPStatus.OK),
            f'/group/{cls.group.slug}/': (
                'posts/group_list.html', HTTPStatus.OK
            ),
            cls.URL_PROFILE_AUTHOR: (
                'posts/profile.html', HTTPStatus.OK
            ),
            cls.URL_POST_ID: (
                'posts/post_detail.html', HTTPStatus.OK
            ),
            f'{cls.URL_POST_ID}comment/': (
                None, HTTPStatus.FOUND
            ),
            '/create/': ('posts/create_post.html', HTTPStatus.FOUND),
            f'{cls.URL_POST_ID}edit/': (
                'posts/create_post.html', HTTPStatus.FOUND
            ),
            '/follow/': ('posts/follow.html', HTTPStatus.FOUND),
            f'/profile/{cls.not_author}/follow/': (
                None, HTTPStatus.FOUND
            ),
            f'/profile/{cls.not_author}/unfollow/': (
                None, HTTPStatus.FOUND
            ),
            f'{cls.URL_PROFILE_AUTHOR}avatar/': (
                'posts/avatar.html', HTTPStatus.FOUND
            ),
            '/unexisting_page/': ('core/404.html', HTTPStatus.NOT_FOUND),
        }
        cls.url_status_for_author = {
            f'{cls.URL_POST_ID}comment/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK,
            f'{cls.URL_POST_ID}edit/': HTTPStatus.OK,
            f'{cls.URL_POST_ID}delete/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.OK,
            f'/profile/{cls.not_author}/follow/': HTTPStatus.FOUND,
            f'/profile/{cls.not_author}/unfollow/': HTTPStatus.FOUND,
            f'{cls.URL_PROFILE_AUTHOR}avatar/': HTTPStatus.OK,
        }
        cls.repeat_url_redirect = {
            f'{cls.URL_POST_ID}comment/': cls.URL_POST_ID,
            f'{cls.URL_PROFILE_AUTHOR}follow/': cls.URL_PROFILE_AUTHOR,
            f'{cls.URL_PROFILE_AUTHOR}unfollow/': cls.URL_PROFILE_AUTHOR,
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
        redirected_urls = (
            f'{self.URL_POST_ID}comment/',
            '/create/',
            f'{self.URL_POST_ID}edit/',
            f'{self.URL_POST_ID}delete/',
            '/follow/',
        )
        for url in redirected_urls:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, self.REDIRECT_AUTH_LOGIN + url)

    def test_post_url_redirect_not_author_on_post_detail(self):
        """Проверяем редиректы для авторизованного пользователя не автора
        поста"""
        url_redirect = {
            f'{self.URL_POST_ID}edit/': self.URL_POST_ID,
            f'{self.URL_POST_ID}delete/': self.URL_POST_ID,
            f'{self.URL_PROFILE_AUTHOR}avatar/': self.URL_PROFILE_AUTHOR,
        }
        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.not_author_client.get(url, follow=True)
                self.assertRedirects(response, redirect)
        for url, redirect in self.repeat_url_redirect.items():
            with self.subTest(url=url):
                response = self.author_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_post_url_redirect_author(self):
        """Проверяем редиректы для авторизованного автора поста"""
        for url, redirect in self.repeat_url_redirect.items():
            with self.subTest(url=url):
                response = self.author_client.get(url, follow=True)
                self.assertRedirects(response, redirect)
        url = f'{self.URL_POST_ID}delete/'
        response = self.author_client.get(url, follow=True)
        self.assertRedirects(response, self.URL_PROFILE_AUTHOR)

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        for url in self.url_template_status:
            template, _ = self.url_template_status[url]
            with self.subTest(url=url):
                if url not in (f'{self.URL_POST_ID}comment/',
                               f'/profile/{self.not_author}/follow/',
                               f'/profile/{self.not_author}/unfollow/'
                               ):
                    response = self.author_client.get(url)
                    self.assertTemplateUsed(response, template)
