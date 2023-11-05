from modeltranslation.translator import translator, TranslationOptions, register
from .models import Platform

@register(Platform)
class PlatformTranslationOptions(TranslationOptions):
    fields = ('description',)