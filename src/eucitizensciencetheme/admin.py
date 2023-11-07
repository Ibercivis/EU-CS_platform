from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

# Register your models here.

from .models import TopBar, Footer

# A new class to store the top bar
class TopBarAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'slug', 'position','parent')
    ordering = ["-position"]
    pass

class FooterAdmin(TabbedTranslationAdmin):
    list_display = ('description',)
    pass

admin.site.register(TopBar, TopBarAdmin)
admin.site.register(Footer, FooterAdmin)
