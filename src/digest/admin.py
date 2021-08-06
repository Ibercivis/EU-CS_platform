from django.contrib import admin, messages
from django.utils.html import mark_safe
from django.core.mail import EmailMessage
from django.utils.translation import ngettext

from dateutil.relativedelta import relativedelta

from .models import Digest
from blog.models import Post
from events.models import Event
from projects.models import Project
from resources.models import Resource
from organisations.models import Organisation
from .views import showDigest

# Register your models here.


class DigestAdmin(admin.ModelAdmin):
    model = Digest

    actions = ['send_test', 'send_digest']

    def send_digest(self, request, queryset):
        queryset.update(status='p')

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
                'sent']

    def link(self, obj):
        link = '<a href="/showDigest/%s">%s</a>' % (obj.pk, obj.slug)
        return mark_safe(link)

    def send_test(self, request, queryset):
        # TODO: send all test messages
        item = queryset.first()
        subject = '[TEST EU-Citizen.Science] Digest from %s to %s' % (item.dateOrg, item.dateEnd)
        message = showDigest(request, item.id, mode='string')
        to = [request.user.email , 'frasanz@icloud.com', 'frasanz@outlook.com']
        email = EmailMessage(subject, message, to=to)
        email.content_subtype = "html"
        email.send()
        nmessages = 1

        self.message_user(request, ngettext(
            '%d test email was sent',
            '%d test mails were sent',
            nmessages,
            ) % nmessages, messages.SUCCESS)
    send_test.short_description = "Send test to your email address"


admin.site.register(Digest, DigestAdmin)
