from modeltranslation.translator import translator, TranslationOptions, register
from .models import Event

@register(Event)
class EventTranslationOption(TranslationOptions):
    fields = ('description', )
    