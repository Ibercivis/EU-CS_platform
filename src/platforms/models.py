from django.contrib.gis.db import models
from django.conf import settings
from organisations.models import Organisation
from django_countries.fields import CountryField
# Create your models here.

# TODO: This as field and not as choicem and the translation
GEOGRAPHIC_EXTEND_CHOICES = (
    ("GLOBAL", "Global"),
    ("MACRO-REGIONAL", "Macro-regional"),
    ("NATIONAL", "National"),
    ("SUB-NATIONAL", "Sub-national"),
    ("REGIONAL", "Regional"),
    ("CITY", "City"),
    ("NEIGHBOURHOOD", "Neighbourhood"))


class HelpText(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    paragraph = models.TextField()


class Platform(models.Model):
    # Main information
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='platform_creator')
    dateCreated = models.DateTimeField('Created date', auto_now_add=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    description = models.TextField()
    geographicExtend = models.CharField(
        max_length=15,
        choices=GEOGRAPHIC_EXTEND_CHOICES)
    countries = CountryField(multiple=True)
    platformLocality = models.CharField(max_length=300, null=True, blank=True)

    # Contact information
    contactPoint = models.CharField(max_length=100, null=True, blank=True)
    contactPointEmail = models.EmailField(
        max_length=100, null=True, blank=True)
    organisation = models.ManyToManyField(Organisation)

    # Geographical scope
    # Images
    logo = models.ImageField(
        upload_to='images/', max_length=300, null=True, blank=True)
    logoCredit = models.CharField(max_length=300, null=True, blank=True)
    profileImage = models.ImageField(
        upload_to='images/', max_length=300, null=True, blank=True)
    profileImageCredit = models.CharField(
        max_length=300, null=True, blank=True)

    approved = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'
