import pytest
from unittest import mock
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from monitor.models import MonitoredURL, UptimeHistory
from monitor.tasks import check_url_status

# The fixture creates the main user


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='12345678',
        email='test@example.com'
    )

# The second user


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        username='anotheruser',
        password='12345678',
        email='another@example.com'
    )


@pytest.fixture
def api_client():
    return APIClient()

# API client with JWT authorization


@pytest.fixture
def auth_client(user, api_client):
    response = api_client.post('/api/token/', {
        'username': user.username,
        'password': '12345678'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

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

# Test: Record is created


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_create_uptime_history(mock_get, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    uptime_history = UptimeHistory.objects.filter(
        monitored_url=monitored_url).first()
    assert uptime_history is not None
    assert uptime_history.status == 'DOWN'

# Test: Get history for user


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_get_history_for_user(
        mock_get,
        auth_client,
        monitored_url,
        another_user):
    MonitoredURL.objects.create(
        user=another_user,
        url='https://anotherexample.com',
        check_interval=1,
        status='DOWN'
    )

    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response
    check_url_status()

    response = auth_client.get(reverse('uptime-history-list'))
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data['results']) == 1
    assert data['results'][0]['url'] == 'https://example.com'

# Test: Sorting history by time


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_history_sorted_by_time(mock_get, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    monitored_url.status = 'UP'
    monitored_url.save()

    check_url_status()

    history_records = UptimeHistory.objects.all()
    assert history_records[0].checked_at <= history_records[1].checked_at

# Test: Filter history by status


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_history_sorted_by_status(mock_get, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response
    check_url_status()

    monitored_url.status = 'UP'
    monitored_url.save()
    mock_get.return_value = mock.Mock(status_code=200)
    check_url_status()

    history_records = UptimeHistory.objects.all()
    assert history_records[0].status == 'DOWN'
    assert history_records[1].status == 'UP'

# Test: Pagination for large history


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_pagination_for_large_history(mock_get, auth_client, user):
    for i in range(25):
        MonitoredURL.objects.create(
            user=user,
            url=f'https://example{i}.com',
            check_interval=5
        )

    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    response = auth_client.get(reverse('uptime-history-list'))
    data = response.json()

    assert 'next' in data
    assert len(data['results']) == 10

# Test: Access only own history


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_access_only_own_history(
        mock_get,
        auth_client,
        monitored_url,
        another_user):
    MonitoredURL.objects.create(
        user=another_user,
        url='https://anotherexample.com',
        check_interval=1,
        status='DOWN'
    )

    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response
    check_url_status()

    response = auth_client.get(reverse('uptime-history-list'))
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(data['results']) == 1
    assert data['results'][0]['url'] == 'https://example.com'

# Test: Update existing history record


@pytest.mark.django_db
@mock.patch('monitor.tasks.requests.get')
def test_update_existing_history_record(mock_get, monitored_url):
    mock_response = mock.Mock(status_code=500)
    mock_get.return_value = mock_response

    check_url_status()

    history = UptimeHistory.objects.get(monitored_url=monitored_url)
    assert history.status == 'DOWN'
