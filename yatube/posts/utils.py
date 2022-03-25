from django.core.paginator import Paginator
from django.conf import settings


def page_obj_create(request, posts):
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
