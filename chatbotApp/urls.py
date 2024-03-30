from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chat_view, name='chatbot'),
    path('login/', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
]