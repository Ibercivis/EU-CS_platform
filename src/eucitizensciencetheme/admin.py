from django.contrib import admin
from django.db import models
from django_ckeditor_5.fields import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin

# Register your models here.

from .models import Footer, HomeSection, TopBar

# A new class to store the top bar
class HomeSectionAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'title', 'position')
    ordering = ["position"]
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }

    pass

class TopBarAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'slug', 'position','parent')
    ordering = ["-position"]
    pass

class FooterAdmin(TabbedTranslationAdmin):
    list_display = ('description',)
    pass

admin.site.register(HomeSection, HomeSectionAdmin)
admin.site.register(TopBar, TopBarAdmin)
admin.site.register(Footer, FooterAdmin)
