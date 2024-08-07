from django.contrib import admin
from .models import Project, Topic, Status, ApprovedProjects, FollowedProjects, HasTag, DifficultyLevel, ParticipationTask, HelpText, ProjectCountry
from django import forms
from django.db import models
from django_select2.forms import Select2MultipleWidget
from django_ckeditor_5.fields import CKEditor5Widget
from modeltranslation.admin import TabbedTranslationAdmin


class DifficultyLevelAdmin(TabbedTranslationAdmin):
    list_display = ('difficultyLevel',)
    pass

class ProjectFormA(forms.ModelForm):
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=Select2MultipleWidget, required=False)

    class Meta:
        model = Project
        exclude = ('origin',)

class HasTagAdmin(TabbedTranslationAdmin):
    list_display = ('hasTag',)
    pass

class ParticipationTaskAdmin(TabbedTranslationAdmin):
    list_display = ('participationTask',)
    pass

class ProjectAdmin(TabbedTranslationAdmin):
    list_filter = ('creator', 'status', )
    form = ProjectFormA

    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

class StatusAdmin(TabbedTranslationAdmin):
    list_display = ('status',)
    pass

class TopicAdmin(TabbedTranslationAdmin):
    list_display = ('topic',)
    pass

class HelpTextAdmin(TabbedTranslationAdmin):
    list_display = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    formfield_overrides = {
        models.TextField: {'widget': CKEditor5Widget(config_name='extends')}
    }
    pass

class ProjectCountryAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'country', 'latitude', 'longitude')
    search_fields = ('country_name', 'country')  # Asumiendo que 'country' es un campo accesible

admin.site.register(DifficultyLevel, DifficultyLevelAdmin)
admin.site.register(HasTag, HasTagAdmin)
admin.site.register(ParticipationTask, ParticipationTaskAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectCountry, ProjectCountryAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(HelpText, HelpTextAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(ApprovedProjects)
admin.site.register(FollowedProjects)

