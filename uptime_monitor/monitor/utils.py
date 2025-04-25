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