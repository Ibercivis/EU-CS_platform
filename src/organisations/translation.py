from modeltranslation.translator import translator, TranslationOptions, register
from .models import Organisation, OrganisationType

@register(Organisation)
class OrganisationTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(OrganisationType)
class OrganisationTypeTranslationOptions(TranslationOptions):
    fields = ('type',)