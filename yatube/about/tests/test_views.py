from django import forms
from django.test import TestCase
from django.urls import reverse

from about.forms import Feedback


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.viewname = 'about:feedback'
        cls.template = 'about/feedback.html'

    def test_pages_uses_correct_templates(self):
        """namespace:name использует соответствующий шаблон."""
        reverse_name = reverse(self.viewname)
        response = self.client.get(reverse_name)
        self.assertTemplateUsed(response, self.template)

    def test_view_feedback_sent_msg(self):
        """Шаблон feedback.html сформирован с правильным контекстом."""
        response = self.client.get(reverse(self.viewname))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], Feedback)
        form_fields = {
            'name': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
