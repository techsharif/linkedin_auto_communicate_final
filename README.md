# Project Title

Linkedin Tool

## Installing

Python 3.6
Django 2.0.3

pip install -r requirements.txt
python manage.py migrate
python manage.py add_membershiptype
python manage.py runserver

## Configure and settings
create a local_settings.py in jetbuzz folder with appropriate values like below:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'sq_jetbuzz_db',
        'USER': '[db user]',
        'PASSWORD': '[db password]',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

## The best is to use virtuall environemtn


## Authors

* **Vasily Jin** - *main work* - [vajin1125](https://github.com/vajin1125)
