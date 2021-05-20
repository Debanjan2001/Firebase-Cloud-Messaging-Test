release: python manage.py makemigrations --no-input
release: python manage.py migrate --no-input
web: gunicorn fcm_test.wsgi --log-file -