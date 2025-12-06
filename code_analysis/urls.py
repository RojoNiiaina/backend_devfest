from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CodeAnalysisViewSet, ResultatViewSet

router = DefaultRouter()
router.register(r'analyses', CodeAnalysisViewSet)
router.register(r'resultats', ResultatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
