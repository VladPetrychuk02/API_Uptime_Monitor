import requests


def send_webhook(webhook_url, url, old_status, new_status):
    payload = {
        'url': url,
        'old_status': old_status,
        'new_status': new_status,
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Webhook sent successfully: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Webhook failed: {e}")
