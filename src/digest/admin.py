from django.contrib import admin
from .models import Digest
from blog.models import Post
from events.models import Event
from projects.models import Project
from resources.models import Resource
from organisations.models import Organisation
from dateutil.relativedelta import relativedelta
from django.utils.html import mark_safe

# Register your models here.


class DigestAdmin(admin.ModelAdmin):
    model = Digest

    class Media:
        js = ("site/js/admin_digest.js",)

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.slug = 'digest_%s_%s' % (obj.dateOrg, obj.dateEnd)
        if obj.includePosts:
            obj.nPosts = Post.objects.filter(
                    status=1,
                    created_on__range=(obj.dateOrg, obj.dateEnd)).count()

        if obj.includeEvents:
            obj.nEvents = Event.objects.filter(
                    approved=True,
                    end_date__range=(obj.dateEnd, obj.dateEnd+relativedelta(months=+2))).count()

        if obj.includeOrganisations:
            obj.nOrganisations = Organisation.objects.filter(
                    dateCreated__range=(obj.dateOrg, obj.dateEnd)).count()

        if obj.includeProjects:
            obj.nProjects = Project.objects.filter(
                    approved=True,
                    dateCreated__range=(obj.dateOrg, obj.dateEnd)).count()

        if obj.includeResources:
            obj.nResources = Resource.objects.filter(
                    isTrainingResource=False,
                    approved=True,
                    dateUploaded__range=(obj.dateOrg, obj.dateEnd)).count()

        if obj.includeTrainings:
            obj.nTrainings = Resource.objects.filter(
                    isTrainingResource=True,
                    approved=True,
                    dateUploaded__range=(obj.dateOrg, obj.dateEnd)).count()
        obj.save()

    def get_list_display(self, request):
        return[
                'pk',
                'link',
                'dateOrg',
                'dateEnd',
                'nPosts',
                'nEvents',
                'nOrganisations',
                'nProjects',
                'nResources',
                'nTrainings',
                'temail',
                'test',
                'send',
                'sent']

    def link(self, obj):
        link = '<a href="/showDigest/%s">%s</a>' % (obj.pk, obj.slug)
        return mark_safe(link)

    def temail(self, obj):
        field = '<input type="text"/>'
        return mark_safe(field)

    def test(self, obj):
        test_button = '<button class="button test">Test</button>'
        return mark_safe(test_button)

    def send(self, obj):
        send_button = '<button class="button">Send</button>'
        return mark_safe(send_button)

    @staticmethod
    def sendTest():
        return 0


admin.site.register(Digest, DigestAdmin)
