from django.contrib import admin
from .models import Project, Category, Status
from django import forms
from django_select2.forms import Select2MultipleWidget


class ProjectFormA(forms.ModelForm):
    topic = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=Select2MultipleWidget, required=False)
    def __init__(self, *args, **kwargs):
        super(ProjectFormA, self).__init__(*args, **kwargs)
        obj = kwargs.get('instance')
        if obj:
            initial = [i for i in obj.topic.split('#')]
            self.initial['topic'] = initial
    class Meta:
        model = Project
        exclude = ('origin',)


class ProjectA(admin.ModelAdmin):
    list_filter = ('creator', 'status', )
    form = ProjectFormA


admin.site.register(Project, ProjectA)
admin.site.register(Category)
admin.site.register(Status)