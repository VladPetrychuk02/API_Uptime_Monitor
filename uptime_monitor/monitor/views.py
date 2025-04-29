from rest_framework import viewsets, permissions, filters

from .permissions import IsOwnerPermission
from .models import MonitoredURL, UptimeHistory
from .serializers import MonitoredURLSerializer, UptimeHistorySerializer


class MonitoredURLViewSet(viewsets.ModelViewSet):
    serializer_class = MonitoredURLSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        return MonitoredURL.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UptimeHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UptimeHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['checked_at']
    search_fields = ['status']

    def get_queryset(self):
        return UptimeHistory.objects.filter(
            monitored_url__user=self.request.user
        ).order_by('-checked_at')
