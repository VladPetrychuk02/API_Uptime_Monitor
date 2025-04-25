import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from monitor.models import MonitoredURL

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

# API client without authorization
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

# Creating a URL that the main user monitors
@pytest.fixture
def monitored_url(user):
    return MonitoredURL.objects.create(
        user=user,
        url='https://google.com',
        check_interval=5
    )

# Test: an authorized user can create a URL
def test_create_monitored_url(auth_client):
    response = auth_client.post('/api/monitor/urls/', {
        "url": "https://example.com",
        "check_interval": 10
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['url'] == 'https://example.com'

# Test: the user sees only their own URLs
def test_only_own_urls_visible(auth_client, monitored_url, another_user):
    MonitoredURL.objects.create(
        user=another_user,
        url='https://evil.com',
        check_interval=5
    )

    response = auth_client.get('/api/monitor/urls/')
    urls = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(urls['results']) == 1
    assert urls['results'][0]['url'] == 'https://google.com'

# Test: other people's URLs are not available
def test_forbidden_to_retrieve_foreign_url(api_client, another_user, monitored_url):
    response = api_client.post('/api/token/', {
        'username': another_user.username,
        'password': '12345678'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    url = f'/api/monitor/urls/{monitored_url.id}/'
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND

# Test: other people's URLs are not available
def test_unauthorized_access(api_client):
    response = api_client.get('/api/monitor/urls/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED