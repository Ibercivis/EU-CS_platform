from django.db import models
from django.conf import settings
from projects.models import Project
from organisations.models import Organisation

class Event(models.Model):
    creator = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            null=True,
            blank=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    place = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date')
    hour = models.TimeField(null=True, blank=True)
    url = models.CharField(max_length=200)
    featured = models.BooleanField(null=True, default=False)
    online_event = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='events_associated')
    mainOrganisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='events_coordinated')
    organisations = models.ManyToManyField(Organisation, blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title


class ApprovedEvents(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.event}'


class UnApprovedEvents(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.event}'
