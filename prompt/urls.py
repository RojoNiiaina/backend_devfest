from django.urls import path
from . import views

urlpatterns = [
    path('ai_prompt/', views.ai_prompt, name='ai_prompt'),
    # path('test-gemini/', views.test_gemini, name='test_gemini'),
]