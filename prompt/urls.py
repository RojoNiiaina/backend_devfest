from django.urls import path
from . import views

urlpatterns = [
    path('ai_prompt/', views.ai_prompt, name='ai_prompt'),
]