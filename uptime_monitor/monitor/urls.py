from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MonitoredURLViewSet, UptimeHistoryViewSet

router = DefaultRouter()
router.register(r'urls', MonitoredURLViewSet, basename='monitored-url')
router.register(r'history', UptimeHistoryViewSet, basename='uptime-history')

urlpatterns = [
    path('', include(router.urls)),
]
