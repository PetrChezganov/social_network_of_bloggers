from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/', views.AboutTechView.as_view(), name='tech'),
    path('feedback/', views.feedback, name='feedback'),
    path('thanks/', views.AboutThanksView.as_view(), name='thanks'),
]
