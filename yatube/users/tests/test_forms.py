from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from users.forms import CreationForm

User = get_user_model()


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def test_user_signup(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()
        self.assertFalse(
            User.objects.filter(
                username='TestName',
                email='testname@gmail.com'
            ).exists()
        )
        form_data = {
            'username': 'TestName',
            'email': 'testname@gmail.com',
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
                username='TestName',
                email='testname@gmail.com'
            ).exists()
        )
