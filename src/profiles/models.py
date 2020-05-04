from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
import uuid
from django.db import models
from django.conf import settings


class InterestArea(models.Model):
    interestArea = models.TextField()
    def __str__(self):        
        return f'{self.interestArea}'

class BaseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    slug = models.UUIDField(default=uuid.uuid4, blank=True, editable=False)
    # Add more user profile fields here. Make sure they are nullable
    # or with default values
    picture = models.ImageField(
        "Profile picture", upload_to="profile_pics/%Y-%m-%d/", null=True, blank=True
    )
    title = models.CharField("Title", max_length=200, blank=True, null=True)
    bio = models.CharField("Short Bio and disciplinary background", max_length=400, blank=True, null=True)
    institution = models.CharField("Institution", max_length=200, blank=True, null=True)
    interestAreas = models.ManyToManyField(InterestArea, blank=True)
    latitude = models.DecimalField(max_digits=9,decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9,decimal_places=6, blank=True, null=True)
    email_verified = models.BooleanField("Email verified", default=False)
    orcid = models.CharField("ORCID", max_length=50, blank=True, null=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Profile(BaseProfile):
    def __str__(self):
        return "{}'s profile".format(self.user)
