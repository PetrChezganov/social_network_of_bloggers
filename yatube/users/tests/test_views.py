from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='TestName',
            email='test@test.com',
            password='1q2w3e4r',
        )
        cls.url_name_template = {
            'users:signup': 'users/signup.html',
            'users:logout': 'users/logged_out.html',
            'users:login': 'users/login.html',
            'users:password_change_form': 'users/password_change_form.html',
            'users:password_change_done': 'users/password_change_done.html',
            'users:password_reset_form': 'users/password_reset_form.html',
            'users:password_reset_done': 'users/password_reset_done.html',
            'users:password_reset_complete': (
                'users/password_reset_complete.html'
            ),
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    # Проверяем используемые шаблоны и корректность namespace:name
    def test_pages_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        for name, template in self.url_name_template.items():
            with self.subTest(template=template):
                reverse_name = reverse(name)
                if (
                    template
                    != 'users/password_change_form.html'
                    and template
                    != 'users/password_change_done.html'
                ):
                    response = self.author_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    # Проверяем используемый шаблон и корректность namespace:name
    # для password_reset_confirm
    def test_password_reset_confirm_uses_correct_templates(self):
        """URL-адрес /auth/reset/<uidb64>/<token>/ использует соответствующий шаблон.
        """
        name = 'users:password_reset_confirm'
        kwargs_name = {'uidb64': 'uidb64', 'token': 'token'}
        template = 'users/password_reset_confirm.html'
        reverse_name = reverse(name, kwargs=kwargs_name)
        response = self.author_client.get(reverse_name)
        self.assertTemplateUsed(response, template)

    # Проверяем, что словарь context страницы auth/signup/
    # содержит ожидаемые значения
    def test_user_create_page_show_correct_context(self):
        """Шаблон users/signup.html сформирован с правильным контекстом."""
        response = self.client.get(reverse('users:signup'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CreationForm)
        form_fields = {
            'username': forms.fields.CharField,
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
