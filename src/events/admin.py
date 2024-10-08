from django.contrib import admin
from .models import Event, HelpText
from django.db import models
from django_ckeditor_5.fields import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin

# Register your models here.

class EventAdmin(TabbedTranslationAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

class HelpTextAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'slug',)
    prepopulated_fields = {'slug': ('title',)}
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass



# TODO: Add Event face-to-face etc. to admin (first in model)

admin.site.register(Event, EventAdmin)
admin.site.register(HelpText, HelpTextAdmin)
