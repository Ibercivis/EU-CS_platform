from django.contrib import admin
from django import forms
from modeltranslation.admin import TabbedTranslationAdmin
from django.db import models   
from django_ckeditor_5.fields import CKEditor5Widget
from .models import  HelpText, Platform

# Register your models here.

class HelpTextAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'slug',)
    prepopulated_fields = {'slug': ('title',)}
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass


class PlatformAdminForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = "__all__"

class PlatformAdmin(TabbedTranslationAdmin):
    forms = PlatformAdminForm
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

admin.site.register(HelpText, HelpTextAdmin)
admin.site.register(Platform, PlatformAdmin)

