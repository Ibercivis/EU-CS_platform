

# EU-CS_platform

EU-CS_platform is a web platform for Citizen Science. It is built with [Python][0] using the [Django Web Framework][1].


## Installation
First of all, install Python v3 <br/>

Once you have python in your SO, download or clone this repository and launch next commands.<br/>
```
python -m pip install --upgrade pip
```
```
pip install -U django
```

Configure a Database. IE a PostgreSQL DB and configure database section in \src\eucs_platform\settings\base.py with the correct data.

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
And for do this automatically:
python manage.py crontab add
```


[0]: https://www.python.org/
[1]: https://www.djangoproject.com/
