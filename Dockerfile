FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

RUN python manage.py migrate

EXPOSE 8000

CMD ["gunicorn", "ecommerce_platform.wsgi:application", "--bind", "0.0.0.0:8000"]