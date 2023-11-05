from django.contrib import admin
from django import forms
from modeltranslation.admin import TabbedTranslationAdmin
from ckeditor.widgets import CKEditorWidget
from .models import Platform

# Register your models here.


class PlatformAdminForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = "__all__"

class MyPlatformAdmin(TabbedTranslationAdmin):
    forms = PlatformAdminForm
    pass

admin.site.register(Platform, MyPlatformAdmin)

