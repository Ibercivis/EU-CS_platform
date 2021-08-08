from django.contrib.gis.db import models
from django.conf import settings
from django_countries.fields import CountryField


class OrganisationType(models.Model):
    type = models.TextField()

    def __str__(self):
        return f'{self.type}'


class Organisation(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator')
    dateCreated = models.DateTimeField('Created date', auto_now=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    description = models.CharField(max_length=3000)
    orgType = models.ForeignKey(OrganisationType, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    contactPoint = models.CharField(max_length=100, null=True, blank=True)
    contactPointEmail = models.EmailField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location = models.PointField(blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    country = CountryField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class OrganisationPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
