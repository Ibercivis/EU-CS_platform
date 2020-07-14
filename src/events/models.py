from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    place = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date')
    hour = models.TimeField(null=True, blank=True)
    url = models.CharField(max_length=200)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title