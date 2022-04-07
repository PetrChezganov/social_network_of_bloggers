from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='TestName',
            email='test@test.com',
            password='1q2w3e4r',
        )
        cls.url_template_status = {
            '/auth/signup/': ('users/signup.html', HTTPStatus.OK),
            '/auth/logout/': (
                'users/logged_out.html', HTTPStatus.OK
            ),
            '/auth/login/': ('users/login.html', HTTPStatus.OK),
            '/auth/password_change/': (
                'users/password_change_form.html', HTTPStatus.FOUND
            ),
            '/auth/password_change/done/': (
                'users/password_change_done.html', HTTPStatus.FOUND
            ),
            '/auth/password_reset/': (
                'users/password_reset_form.html', HTTPStatus.OK
            ),
            '/auth/password_reset/done/': (
                'users/password_reset_done.html', HTTPStatus.OK
            ),
            '/auth/reset/<uidb64>/<token>/': (
                'users/password_reset_confirm.html', HTTPStatus.OK
            ),
            '/auth/reset/done/': (
                'users/password_reset_complete.html', HTTPStatus.OK
            ),
        }
        cls.REDIRECT_AUTH_LOGIN = '/auth/login/?next='

    def setUp(self):
        # print(author)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    # Проверяем общедоступные страницы
    def test_urls_exists_at_desired_location(self):
        for url in self.url_template_status:
            _, status = self.url_template_status[url]
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    # Проверяем доступность страниц для авторизованного автора поста
    def test_urls_exists_at_desired_location_authorized(self):
        url_status = {
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
        }
        for url, status in url_status.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, status)

    # Проверяем редиректы для неавторизованного пользователя
    def test_password_change_url_redirect_anonymous_on_admin_login(self):
        redirected_urls = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for url in redirected_urls:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertRedirects(response, self.REDIRECT_AUTH_LOGIN + url)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        for url in self.url_template_status:
            template, _ = self.url_template_status[url]
            with self.subTest(url=url):
                response = self.author_client.get(url)
                if (
                    self.url_template_status[url][0]
                    != 'users/password_change_form.html'
                    and self.url_template_status[url][0]
                    != 'users/password_change_done.html'
                ):
                    self.assertTemplateUsed(response, template)
