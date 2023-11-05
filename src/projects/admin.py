from django.contrib import admin
from .models import Project, Topic, Status, ApprovedProjects, FollowedProjects, HasTag
from django import forms
from django_select2.forms import Select2MultipleWidget
from ckeditor.widgets import CKEditorWidget

class ProjectFormA(forms.ModelForm):
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=Select2MultipleWidget, required=False)
    description = forms.CharField(widget=CKEditorWidget())
    aim = forms.CharField(widget=CKEditorWidget())
    description_citizen_science_aspects = forms.CharField(widget=CKEditorWidget())
    how_to_participate = forms.CharField(widget=CKEditorWidget())
    equipment = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Project
        exclude = ('origin',)


class ProjectA(admin.ModelAdmin):
    list_filter = ('creator', 'status', )
    form = ProjectFormA


admin.site.register(Project, ProjectA)
admin.site.register(Topic)
admin.site.register(Status)
admin.site.register(ApprovedProjects)
admin.site.register(FollowedProjects)
admin.site.register(HasTag)
