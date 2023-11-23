from modeltranslation.translator import translator, TranslationOptions, register
from .models import HelpText, Platform

@register(HelpText)
class HelpTextTranslationOptions(TranslationOptions):
    fields = ('title', 'paragraph',)

@register(Platform)
class PlatformTranslationOptions(TranslationOptions):
    fields = ('description',)