# API Uptime Monitor

## Project Description

**API Uptime Monitor** is a tool for monitoring the availability of APIs or websites. It checks the status of the specified URLs, sends alerts to users when the status changes (e.g., a site goes down or comes back up), and stores the status change history for further analysis.

This project includes:
- **REST API** for registering and managing URL monitoring.
- **Periodic checks** of URL status using **Celery**.
- Alerts via **Email** and **Webhook**.
- Storing status history as a time series, accessible via the API.

## Technologies Used

- **FastAPI** — for building a high-performance REST API.
- **Celery** — for asynchronous tasks and periodic checks.
- **Redis** — for managing queues of tasks that are executed asynchronously
- **PostgreSQL** — for storing data (URLs, status history).
- **Docker** — for containerizing the application and database.
- **Celery Beat** — for scheduling periodic tasks.

## Features of the Project

1. **User Dashboard / REST API to Register URLs**:
   - Register and manage URLs through the REST API.
   - Add, update, and delete monitored URLs.
   - View a list of the user's monitored URLs.

2. **Periodic Health Checks using Celery**:
   - Periodic status checks for URLs (e.g., every 5 or 10 minutes).
   - Automatic site availability checks via HTTP requests.

3. **Email or Webhook Alerts**:
   - Email notifications when the status of a URL changes (e.g., from "UP" to "DOWN" and vice versa).
   - Ability to set up a **Webhook** to receive notifications via HTTP POST requests.

4. **Uptime History as a Time Series**:
   - Storing the status change history of URLs as a time series.
   - Access to history via the REST API (filtering, sorting, pagination).

## Installation and Setup Guide

### Technical requirements
Before starting, it is advisable to check for the presence of these programs
- Python (3.10+)
- Docker (4.30.0+)
- PostgreSQL
- Redis
- Celery

### 1. Clone the repository

```
git clone https://github.com/VladPetrychuk02/API_Uptime_Monitor
cd API_Uptime_Monitor
```
2. Create and activate a virtual environment
```
python3 -m venv venv
source venv/bin/activate  # Для Linux
venv/Scripts/activate  # Для Windows
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Set up Docker
- Install **Docker** and **Docker Compose** if they are not already installed.
- Use **docker-compose** to launch containers:
```
docker-compose build
docker-compose up -d
```

This command will start:
- PostgreSQL (for storing data).
- Redis (for use with Celery).
- Celery (to check the availability of sites at a given interval).
- Celery Beat (execution of tasks according to a certain schedule).
- FastAPI web server.

### 5. Install dependencies inside Docker containers
```
docker-compose exec web pip install -r requirements.txt
```

### 6. Run database migrations
```
docker-compose exec web alembic upgrade head
```

### 7. Access the API

- **API endpoints**:
  - URLs: `http://127.0.0.1:8000/api/monitor/urls/`
  - Uptime History: `http://127.0.0.1:8000/api/monitor/history/`
  - Register page: `http://127.0.0.1:8000/auth/register/`
  - Getting users token: `http://127.0.0.1:8000/api/users/token`
  - URLs stats: `http://127.0.0.1:8000/api/monitor/stats/`
  - Run 'check status' task: `http://127.0.0.1:8000/run-task/`

## Important Notes:
- To work with Webhook notifications, specify the Webhook URL when adding a URL to check.
Example:
```
{
    "url": "https://example.com",
    "check_interval": 5
    "webhook_url": "your-webhook-url"
}
```
