


# EU-CS_platform

EU-CS_platform is a web platform for Citizen Science. It is built with [Python][0] using the [Django Web Framework][1].

## Requirements

```bash
$ sudo apt install python3-venv python3-pip libpq-dev postgresql postgresql-10-postgis-2.4 gettext
$ python3 -m venv venv
$ source venv/bin/activate
```

## Configure postgres

```bash
$ su - postgres
$ psql
postgres=# create database eucitizenscience;
postgres=# create user eucitizenscience with password 'XXXXXXXXXXXXXX';
postgres=# grant all on database eucitizenscience to eucitizenscience;
postgres=# \c eucitizenscience
postgres=# create extension postgis;
```

## Installation

First of all, check whether you've up to Requirements.
Second, clone the project with:

```bash
$ git clone https://github.com/Ibercivis/EU-CS_platform ~/EU-CS_platform
$ cd EU-CS_platform
$ pip install -r requirements.txt
```
    
```bash
$ cd src
$ cp eucs_platform/settings/local.sample.reference.env eucs_platform/settings/local.env
```

And edit `src/eucs_platform/settings/local.env` with database and email and other configuration variables

```bash
$ python manage.py migrate
```

Now, create superuser
```
$ python3 manage.py createsuperuser
```

```bash
python manage.py loaddata ./organisations/fixtures/organisation_types.json
python manage.py loaddata ./projects/fixtures/participationtasks.json
python manage.py loaddata ./projects/fixtures/status.json
python manage.py loaddata ./projects/fixtures/topics.json
python manage.py loaddata ./projects/fixtures/difficultylevel.json
python manage.py loaddata ./projects/fixtures/hastag.json
python manage.py loaddata ./projects/fixtures/geographicextend.json
python manage.py loaddata ./resources/fixtures/audiences.json
python manage.py loaddata ./resources/fixtures/themes.json
python manage.py loaddata ./resources/fixtures/categories.json
```


## Launch
```bash
$ python manage.py runserver
```

## Cron jobs commands

Manually:

```bash
$ python manage.py runcrons
$ python manage.py runcrons --force
```

And to do this automatically:

```bash
$ python manage.py crontab add
```


[0]: https://www.python.org/
[1]: https://www.djangoproject.com/
