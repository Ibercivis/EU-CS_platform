from django.contrib import admin
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from .models import Pages
from django import forms
from django_ckeditor_5.fields import CKEditor5Widget
from django.db import models
from modeltranslation.admin import TabbedTranslationAdmin
from django.shortcuts import render, reverse, get_object_or_404


# Register your models here.

class PagesAdminForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = "__all__"

class MyTransatedPagesAdmin(TabbedTranslationAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'created_on')
    
    # set content widget to ckeditor5
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

admin.site.register(Pages, MyTransatedPagesAdmin)

