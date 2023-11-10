from django.contrib import admin
from .models import Audience, Category, EducationLevel, LearningResourceType,  Resource, ResourceGroup, ResourcesGrouped, ApprovedResources, SavedResources, Theme
from django.db import models
from django_ckeditor_5.fields import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin


class AudienceAdmin(TabbedTranslationAdmin):
    list_display = ('audience',)
    pass

class CategoryAdmin(TabbedTranslationAdmin):
    list_filter = ('text', 'parent',)
    ordering = ('-parent',)
    pass

class EducationLevelAdmin(TabbedTranslationAdmin):
    list_display = ('educationLevel',)
    pass

class LearningResourceTypeAdmin(TabbedTranslationAdmin):
    list_display = ('learningResourceType',)
    pass

class ResourceAdmin(TabbedTranslationAdmin):
    list_filter = ('creator', 'category' )
    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

class ResourcesGroupedAdmin(admin.ModelAdmin):
    list_filter = ('group', 'resource',)
    ordering = ('-group',)

class ThemeAdmin(TabbedTranslationAdmin):
    list_filter = ('theme',)
    pass

admin.site.register(Audience, AudienceAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(EducationLevel, EducationLevelAdmin)
admin.site.register(LearningResourceType, LearningResourceTypeAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceGroup)
admin.site.register(ResourcesGrouped, ResourcesGroupedAdmin)
admin.site.register(ApprovedResources)
admin.site.register(SavedResources)
admin.site.register(Theme, ThemeAdmin)
