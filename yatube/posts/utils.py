from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator


def page_obj_create(request, posts):
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def send_msg(name, email, text):
    subject = f"Обратная связь от {name}"
    body = f"{text}"
    send_mail(
        subject, body, email, ["real84work@mail.ru", ],
    )
