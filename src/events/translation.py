from modeltranslation.translator import translator, TranslationOptions, register
from .models import Event, HelpText

@register(HelpText)
class HelpTextTranslationOptions(TranslationOptions):
    fields = ('title', 'paragraph',)

@register(Event)
class EventTranslationOption(TranslationOptions):
    fields = ('description', )
    