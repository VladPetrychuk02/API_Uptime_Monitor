from rest_framework import serializers
from .models import MonitoredURL, UptimeHistory


class MonitoredURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoredURL
        fields = '__all__'
        read_only_fields = ['id', 'user',
                            'status', 'created_at', 'last_checked']


class UptimeHistorySerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='monitored_url.url', read_only=True)

    class Meta:
        model = UptimeHistory
        fields = ['id', 'url', 'status', 'checked_at']
