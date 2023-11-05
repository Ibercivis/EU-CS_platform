from modeltranslation.translator import translator, TranslationOptions, register
from .models import Pages

@register(Pages)
class PagesTranslationOptions(TranslationOptions):
    fields = ('name', 'content',)


