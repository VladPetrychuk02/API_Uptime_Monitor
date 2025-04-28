import pytest
from unittest import mock
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import User
from monitor.models import MonitoredURL
from monitor.tasks import check_url_status

# The fixture creates the main user
@pytest.fixture
def user(db):
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
        status='UNKNOWN'
    )

# Test: status becomes UP
@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_status_becomes_up(mock_get, monitored_url):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    check_url_status()

    monitored_url.refresh_from_db()
    assert monitored_url.status == 'UP'

# Test: status becomes DOWN
@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_status_becomes_down(mock_get, monitored_url):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    check_url_status()

    monitored_url.refresh_from_db()
    assert monitored_url.status == 'DOWN'

# Test: check for missing check before interval
@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_skip_check_before_interval(mock_get, monitored_url):
    monitored_url.last_checked = now() + timedelta(minutes=1)
    monitored_url.save()
    monitored_url.refresh_from_db()

    check_url_status()

    assert mock_get.call_count == 0

# Test: status becomes DOWN on request error
@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get', side_effect=Exception('Connection error'))
def test_status_becomes_down_on_error(mock_get, monitored_url):
    check_url_status()

    monitored_url.refresh_from_db()
    assert monitored_url.status == 'DOWN'

# Test: update last_checked after check
@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_last_checked_updated(mock_get, monitored_url):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    assert monitored_url.last_checked is None

    check_url_status()

    monitored_url.refresh_from_db()
    assert monitored_url.last_checked is not None