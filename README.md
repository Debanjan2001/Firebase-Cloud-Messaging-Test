Create VirtualEnv
```
python -m virtualenv env
```

Activate Environment
```
source env/bin/activate
```

Install Dependencies 
```
pip install -r requirements.txt
```

Run migrations.
```
python manage.py migrate
python manage.py makemigrations
```

Create SuperUser
```
python manage.py createsuperuser
```

Run dev-server
```
python manage.py runserver
```

Go to http://127.0.0.1:8080/
Explore the api root. Register some devices using different browser generated tokens and start testing messaging.
