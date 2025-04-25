from rest_framework import viewsets, permissions
from .models import MonitoredURL
from .serializers import MonitoredURLSerializer

class MonitoredURLViewSet(viewsets.ModelViewSet):
    serializer_class = MonitoredURLSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MonitoredURL.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)