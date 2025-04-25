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