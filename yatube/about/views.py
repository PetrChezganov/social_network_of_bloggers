from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

from about.forms import Feedback
from posts.utils import send_msg


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'


class AboutThanksView(TemplateView):
    template_name = 'about/thanks.html'


def feedback(request):
    form = Feedback(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        text = form.cleaned_data['text']
        send_msg(name, email, text)
        return redirect('about:thanks')
    return render(request, 'about/feedback.html', {'form': form})
