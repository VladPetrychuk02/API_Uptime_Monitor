from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MonitoredURL(models.Model):
    STATUS_CHOICES = (
        ('UP', 'UP'),
        ('DOWN', 'DOWN'),
        ('UNKNOWN', 'UNKNOWN'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="urls")
    url = models.URLField()
    check_interval = models.IntegerField(default=5, help_text="Check interval in minutes")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNKNOWN')
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(null=True, blank=True)

    webhook_url = models.URLField(null=True, blank=True, help_text="Optional webhook for alerts")

    def __str__(self):
        return f"{self.url} ({self.status})"
    
class UptimeHistory(models.Model):
    monitored_url = models.ForeignKey(MonitoredURL, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=10, choices=MonitoredURL.STATUS_CHOICES)
    checked_at = models.DateTimeField()

    def __str__(self):
        return f"{self.monitored_url.url} was {self.status} at {self.checked_at}"