from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from monitor.models import UptimeHistory


class ClearHistoryMixin:
    @action(detail=False, methods=["delete"], permission_classes=[IsAuthenticated])
    def clear_history(self, request):
        UptimeHistory.objects.filter(monitored_url__user=request.user).delete()

        return Response(
            {"message": "History cleared successfully!"},
            status=status.HTTP_204_NO_CONTENT
        )
