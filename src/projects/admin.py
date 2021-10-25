from django.contrib import admin
from .models import Project, Topic, Status, ApprovedProjects, FollowedProjects
from django import forms
from django_select2.forms import Select2MultipleWidget


class ProjectFormA(forms.ModelForm):
    topic = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=Select2MultipleWidget, required=False)

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
