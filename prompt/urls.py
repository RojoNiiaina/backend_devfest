from django.urls import path
from . import views

urlpatterns = [
    path('ai_prompt/', views.ai_prompt, name='ai_prompt'),
    path('prompts-list/', views.get_prompts_list, name='get_prompts_list'),
]