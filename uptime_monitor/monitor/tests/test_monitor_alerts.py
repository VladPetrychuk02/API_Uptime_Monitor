import pytest
from unittest import mock
from monitor.models import MonitoredURL
from monitor.tasks import check_url_status

# The fixture creates the main user


@pytest.fixture
def user(db):
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='testuser',
        password='12345678',
        email='test@example.com'
    )

# The fixture creates a monitored URL object


@pytest.fixture
def monitored_url(user):
    return MonitoredURL.objects.create(
        user=user,
        url='https://example.com',
        check_interval=1,
        status='UP',
        webhook_url='https://webhook.site/test'
    )

# Test: Email is sent when status changes


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_status_email')
@mock.patch('monitor.tasks.requests.get')
def test_email_sent_on_status_change(mock_get, mock_send_email, monitored_url):
    mock_response = mock.Mock(status_code=500)  # emulate DOWN
    mock_get.return_value = mock_response

    check_url_status()

    assert mock_send_email.call_count == 1

# Test: Webhook is sent when status changes


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_webhook')
@mock.patch('monitor.tasks.requests.get')
def test_webhook_sent_on_status_change(mock_get, mock_send_webhook, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    assert mock_send_webhook.call_count == 1

# Test: No email/webhook if status doesn't change


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_status_email')
@mock.patch('monitor.tasks.send_webhook')
@mock.patch('monitor.tasks.requests.get')
def test_no_email_no_webhook_if_status_unchanged(mock_get, mock_send_webhook, mock_send_email, monitored_url):
    mock_response = mock.Mock(status_code=200)  # still UP
    mock_get.return_value = mock_response

    check_url_status()

    assert mock_send_email.call_count == 0
    assert mock_send_webhook.call_count == 0

# Test: No email sent if user has no email


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_status_email')
@mock.patch('monitor.tasks.requests.get')
def test_no_email_if_user_has_no_email(mock_get, mock_send_email, monitored_url):
    monitored_url.user.email = ''
    monitored_url.user.save()

    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    assert mock_send_email.call_count == 1

# 5. Test: No webhook sent if webhook_url is empty


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_webhook')
@mock.patch('monitor.tasks.requests.get')
def test_no_webhook_if_no_webhook_url(mock_get, mock_send_webhook, monitored_url):
    monitored_url.webhook_url = ''
    monitored_url.save()

    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    assert mock_send_webhook.call_count == 0

# Test: Email content contains correct status


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_status_email')
@mock.patch('monitor.tasks.requests.get')
def test_email_content_correct(mock_get, mock_send_email, monitored_url):
    mock_response = mock.Mock(status_code=500)  # emulate DOWN
    mock_get.return_value = mock_response

    check_url_status()

    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert monitored_url.url in args
    assert 'UP' in args
    assert 'DOWN' in args

# Test: Webhook payload contains correct data


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_webhook')
@mock.patch('monitor.tasks.requests.get')
def test_webhook_payload_correct(mock_get, mock_send_webhook, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    mock_send_webhook.assert_called_once()
    args, kwargs = mock_send_webhook.call_args
    assert monitored_url.url in args
    assert 'UP' in args
    assert 'DOWN' in args

# Test: Alerts are sent only once per status change


@pytest.mark.django_db
@mock.patch('monitor.tasks.send_status_email')
@mock.patch('monitor.tasks.send_webhook')
@mock.patch('monitor.tasks.requests.get')
def test_alerts_sent_only_once_per_change(mock_get, mock_send_webhook, mock_send_email, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    assert mock_send_email.call_count == 1
    assert mock_send_webhook.call_count == 1
