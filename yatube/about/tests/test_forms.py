from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class FeedbackFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_form_feedback_sent_msg(self):
        """Валидная форма отправляет обратную связь."""
        form_data = {
            'name': 'TestName',
            'email': 'test@test.com',
            'text': 'Тестовая отправка',
        }
        response = self.client.post(
            reverse('about:feedback'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse('about:thanks')
        )
