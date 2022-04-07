from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()
        cls.test_username = 'TestName'
        cls.test_email = 'testname@gmail.com'

    def test_user_signup(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()

        self.assertFalse(
            User.objects.filter(
                username=self.test_username,
                email=self.test_email
            ).exists()
        )
        form_data = {
            'username': self.test_username,
            'email': self.test_email,
            'password1': 'Password_12345',
            'password2': 'Password_12345',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # print(response)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username=self.test_username,
                email=self.test_email
            ).exists()
        )
