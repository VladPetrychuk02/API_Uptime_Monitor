from django.core.mail import send_mail

def send_status_email(user_email, url, old_status, new_status):
    subject = f"Status Change Alert for {url}"
    message = f"The status of {url} has changed from {old_status} to {new_status}."
    send_mail(
        subject,
        message,
        'monitor@uptime.com',
        [user_email],
        fail_silently=False,
    )
    
def send_webhook(webhook_url, url, old_status, new_status):
    payload = {
        'url': url,
        'old_status': old_status,
        'new_status': new_status,
    }
    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Webhook failed: {e}")