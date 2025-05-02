FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/code/uptime_monitor

WORKDIR /code

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install psycopg2-binary

COPY . .

CMD ["uvicorn", "uptime_monitor.main:app", "--host", "0.0.0.0", "--port", "8000"]