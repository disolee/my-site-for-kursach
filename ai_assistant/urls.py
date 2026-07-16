from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/feedback/', views.feedback_api, name='feedback_api'),
]