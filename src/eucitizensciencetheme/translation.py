from modeltranslation.translator import translator, TranslationOptions, register
from .models import TopBar, Footer

@register(TopBar)
class TopBarTranslationOptions(TranslationOptions):
    fields = ('name', )

@register(Footer)
class FooterTranslationOptions(TranslationOptions):
    fields = ('description', 'link_name1', 'link_name2', 'link_name3', 'link_name4', 'link_name5', 'link_name6', 'link_name7', 'link_name8')
