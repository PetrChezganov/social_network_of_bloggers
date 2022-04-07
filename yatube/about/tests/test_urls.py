from http import HTTPStatus

from django.test import TestCase


class AboutUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_template_status = {
            '/about/author/': ('about/author.html', HTTPStatus.OK),
            '/about/tech/': ('about/tech.html', HTTPStatus.OK),
            '/about/thanks/': ('about/thanks.html', HTTPStatus.OK),
            '/about/feedback/': ('about/feedback.html', HTTPStatus.OK),
        }

    def test_urls_exists_at_desired_location(self):
        """Проверяем общедоступные страницы"""
        for url in self.url_template_status:
            _, status = self.url_template_status[url]
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        for url in self.url_template_status:
            template, _ = self.url_template_status[url]
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
