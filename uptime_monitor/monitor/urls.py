from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonitoredURLViewSet

router = DefaultRouter()
router.register(r'urls', MonitoredURLViewSet, basename='monitored-url')

urlpatterns = [
    path('', include(router.urls)),
]