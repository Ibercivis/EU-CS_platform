from django.contrib import admin
from .models import Organisation, OrganisationType
from django.db import models
from django_ckeditor_5.fields import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin


class OrganisationAdmin(TabbedTranslationAdmin):
    list_filter = ('orgType',)
    ordering = ('-name',)
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }

class OrganisationTypeAdmin(TabbedTranslationAdmin):
    list_display = ('type',)
    pass

admin.site.register(OrganisationType, OrganisationTypeAdmin)
admin.site.register(Organisation, OrganisationAdmin)
