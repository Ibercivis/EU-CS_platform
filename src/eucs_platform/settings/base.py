"""
Django settings for eucs_platform project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from django.urls import reverse_lazy
from machina import MACHINA_MAIN_TEMPLATE_DIR, MACHINA_MAIN_STATIC_DIR
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / "directory"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATICFILES_DIRS = [str(BASE_DIR / "static"), MACHINA_MAIN_STATIC_DIR]
MEDIA_ROOT = str(BASE_DIR / "media")
MEDIA_URL = "/media/"
STATIC_ROOT= "/home/ubuntu/v0.2/static"

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp',
    },
}

# Use Django templates using the new Django 1.8 TEMPLATES settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(BASE_DIR / "templates"),
            MACHINA_MAIN_TEMPLATE_DIR
            # insert more TEMPLATE_DIRS here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.request',
                # Machina
                'machina.core.context_processors.metadata',

            ]
        },
    }
]

# Use 12factor inspired environment variables or from a file
import environ

env = environ.Env()

# Create a local.env file in the settings directory
# But ideally this env file should be outside the git repo
env_file = Path(__file__).resolve().parent / "local.env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "authtools",
    "crispy_forms",
    "easy_thumbnails",
    "profiles",
    "accounts",
    "projects",
    "resources",
    "django_select2",
    "blog",
    "django_summernote",
    "leaflet",
    "django_countries",
    "authors",
    "contact",
    "reviews",
    'django.contrib.sites',
    'cookielaw',
    'events',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'rest_framework_swagger',
    'oidc_provider',
    'drf_yasg',
    'captcha',
    'active_link',

    # Machina dependencies:
    'mptt',
    'haystack',
    'widget_tweaks',

    # Machina apps:
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',

    'organisations',
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Machina
    'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
]

ROOT_URLCONF = "eucs_platform.urls"

WSGI_APPLICATION = "eucs_platform.wsgi.application"

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env("DATABASE_NAME"),
            'USER': env("DATABASE_USER"),
            'PASSWORD': env("DATABASE_PASSWORD"),
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGE_CODES = [
    'fr',
    'en',
    'ar',
    'am',
    'bg',
    'bn',
    'ca',
    'cs',
    'da',
    'de',
    'el',
    'es',
    'et',
    'fa',
    'fi',
    'fil',
    'gu',
    'he',
    'hi',
    'hr',
    'hu',
    'id',
    'ga',
    'it',
    'ja',
    'kn',
    'ko',
    'lt',
    'lv',
    'ml',
    'mr',
    'ms',
    'mt',
    'nl',
    'no',
    'pl',
    'pt',
    'ro',
    'ru',
    'sk',
    'sl',
    'sr',
    'sv',
    'sw',
    'ta',
    'te',
    'th',
    'tr',
    'uk',
    'vi',
    'zh_CN'
]

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = "/static/"

ALLOWED_HOSTS = ["*"]

# Crispy Form Theme - Bootstrap 3
CRISPY_TEMPLATE_PACK = "bootstrap3"

# For Bootstrap 3, change error alert to 'danger'
from django.contrib import messages

MESSAGE_TAGS = {messages.ERROR: "danger"}

# Authentication Settings
AUTH_USER_MODEL = "authtools.User"
LOGIN_REDIRECT_URL = reverse_lazy("home")
LOGIN_URL = reverse_lazy("accounts:login")


THUMBNAIL_EXTENSION = "png"  # Or any extn for your thumbnails

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (40.0, -3.0),
    'DEFAULT_ZOOM': 2,
    'MIN_ZOOM': 2,
    'RESET_VIEW': False,
    'MAX_ZOOM': 18,
    #'TILES': [('', 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {'attribution': '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors', 'maxZoom': 20})]

}

SUMMERNOTE_THEME = 'bs4'

SUMMERNOTE_CONFIG = {
    'iframe': True,
    'summernote': {
        'airMode': False,
        'width': '100%',
        'height': '300',
        'toolbar': ['bold', 'italic', 'underline'],
    },
    'disable_attachment': True,
}

#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = env("FROM_EMAIL")
EMAIL_HOST = env("HOST_EMAIL")
EMAIL_HOST_USER = env("FROM_EMAIL")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = '587'
EMAIL_USE_TLS = True

EMAIL_RECIPIENT_LIST = [
    "eucitsci@mfn.berlin",
    "frasanz@bifi.es",
    "mg@margaretgold.co.uk"
]

SITE_ID = 1
REVIEW_PUBLISH_UNMODERATED = True


REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ),
}

PASSWORD_RESET_CONFIRM_URL = '/password-reset/'
ACTIVATION_URL = '/activate/'
DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': '/password-reset/',
    'EMAIL': {
        'activation': 'accounts.views.ActivationEmail',
        'confirmation': 'accounts.views.ConfirmationEmail',
        'password_reset': 'accounts.views.PasswordResetEmail',
    },    
    'SEND_ACTIVATION_EMAIL': True,
}

#OPENID
#LOGIN_URL = '/accounts/login/'
OIDC_SESSION_MANAGEMENT_ENABLE = True

#Swagger
LOGOUT_URL = 'rest_framework:logout'

RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")

#Machina - search for forum conversations
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

MACHINA_BASE_TEMPLATE_NAME = 'base_forum.html'

MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = [
    'can_see_forum',
    'can_read_forum',
    'can_start_new_topics',
    'can_reply_to_topics',
    'can_edit_own_posts',
    'can_post_without_approval',
    'can_create_polls',
    'can_vote_in_polls',
    'can_download_file',
]
