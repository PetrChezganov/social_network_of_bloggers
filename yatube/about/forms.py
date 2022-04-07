from django import forms


class Feedback(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Имя',
        help_text='Введите ваше имя'
    )
    email = forms.EmailField(help_text='Укажите почту для ответа')
    text = forms.CharField(
        widget=forms.Textarea,
        label='Текст',
        help_text='Введите текст'
    )
