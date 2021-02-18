from django.conf import settings


def global_settings(request):
    return {
        'TRANSLATED_LANGUAGES': settings.TRANSLATED_LANGUAGES
    }