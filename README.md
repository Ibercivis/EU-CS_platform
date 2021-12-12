


# EU-CS_platform

EU-CS_platform is a web platform for Citizen Science. It is built with [Python][0] using the [Django Web Framework][1].

## Requirements

```bash
sudo apt install python3-venv
sudo apt install python3-pip
sudo apt install libpq-dev
sudo apt install postgresql
sudo apt install gettext
sudo apt install gettext
python3 -m venv venv
source venv/bin/activate
```

## Configure postgres
create database eucitizenscience
create user eucitizenscience with password 'XXXXXXXXXXXXXX';
grant all on eucitizenscience.* to eucitizenscience
grant all on  database eucitizenscience to eucitizenscience;

## Installation
First of all, install Python v3 <br/>
python3-dev
libpq-dev


In source directory: <br/>
    ```
    pip install -r requirements.txt
    ```
```
cd src
cp eucs_platform/settings/local.sample.reference.env eucs_platform/settings/local.env
And edit this last file with database and email configuration
```

```
python manage.py migrate
```

```
python manage.py loaddata projects/fixtures/topics.json
python manage.py loaddata projects/fixtures/status.json
python manage.py loaddata projects/fixtures/participationtasks.json
python manage.py loaddata projects/fixtures/geographicextend.json
python manage.py loaddata resources/fixtures/categories.json
python manage.py loaddata resources/fixtures/themes.json
python manage.py loaddata resources/fixtures/audiences.json
python manage.py loaddata organisations/fixtures/organisation_types.json
```


## Launch
```
python manage.py runserver
```

## Cron jobs commands
```
python manage.py runcrons
python manage.py runcrons --force
And to do this automatically:
python manage.py crontab add
```


[0]: https://www.python.org/
[1]: https://www.djangoproject.com/
