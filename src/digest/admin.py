from django.contrib import admin
from .models import Digest
from projects.models import Project
from resources.models import Resource
from django.utils.html import mark_safe

# Register your models here.


class DigestAdmin(admin.ModelAdmin):
    model = Digest

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.slug = 'digest_%s_%s' % (obj.dateOrg, obj.dateEnd)
        if obj.hasProjects:
            obj.nProjects = Project.objects.count()
        if obj.hasResources:
            obj.nResources = Resource.objects.count()

        obj.save()

    def get_list_display(self, request):
        return['pk', 'link', 'dateOrg', 'dateEnd', 'nProjects', 'nResources', 'tobeSend', 'sent']

    def link(self, obj):
        link = '<a href="/showDigest/%s">%s</a>' % (obj.pk, obj.slug)
        return mark_safe(link)


admin.site.register(Digest, DigestAdmin)
