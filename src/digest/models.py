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
    tobeSend = models.DateTimeField(null=True, blank=True)
    slug = models.TextField(editable=False, null=True, blank=True)
    hasProjects = models.BooleanField(null=True)
    hasResources = models.BooleanField(null=True)
    nProjects = models.IntegerField(editable=False, null=True, blank=True)
    nResources = models.IntegerField(editable=False, null=True, blank=True)
    sent = models.BooleanField(null=True, editable=False, default=False)

    def __str__(self):
        return f'{self.slug}'
