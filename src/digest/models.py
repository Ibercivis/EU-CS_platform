from django.db import models
from django.conf import settings

# Create your models here.


class Digest(models.Model):
    creator = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            editable=False,
            on_delete=models.DO_NOTHING)
    dateOrg = models.DateField(null=True, blank=True)
    dateEnd = models.DateField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    slug = models.TextField(editable=False, null=True, blank=True)

    includePosts = models.BooleanField(default=True)
    includeEvents = models.BooleanField(default=True)
    includeOrganisations = models.BooleanField(default=True)
    includeProjects = models.BooleanField(default=True)
    includeResources = models.BooleanField(default=True)
    includeTrainings = models.BooleanField(default=True)

    nPosts = models.IntegerField(editable=False, null=True, blank=True)
    nEvents = models.IntegerField(editable=False, null=True, blank=True)
    nOrganisations = models.IntegerField(editable=False, null=True, blank=True)
    nProjects = models.IntegerField(editable=False, null=True, blank=True)
    nResources = models.IntegerField(editable=False, null=True, blank=True)
    nTrainings = models.IntegerField(editable=False, null=True, blank=True)

    sent = models.BooleanField(null=True, editable=False, default=False)

    def __str__(self):
        return f'{self.slug}'
