from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from organisations.models import Organisation, OrganisationType
from django.utils.html import format_html


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
        _("Profile picture"), upload_to="profile_pics/%Y-%m-%d/", null=True, blank=True
    )
    title = models.CharField(_("Title"), max_length=200, blank=True, null=True)
    bio = models.CharField(_("Bio and disciplinary background"), max_length=400, blank=True, null=True)
    interestAreas = models.ManyToManyField(InterestArea, blank=True)
    latitude = models.DecimalField(max_digits=9,decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9,decimal_places=6, blank=True, null=True)
    orcid = models.CharField(_("ORCID (If you have registered on the ORCID platform for researchers and have a persistent digital identifier (your ORCID iD) you can add it here to link this profile with your professional information such as affiliations, grants, publications, peer review, and more.)"), max_length=50, blank=True, null=True)
    organisation = models.ManyToManyField(Organisation,blank=True)

    # ECSA fields
    ecsa_member = models.BooleanField(null=True, blank=True)
    ecsa_requested_join = models.BooleanField(null=True, blank=True)
    ecsa_member_since = models.DateTimeField(null=True,blank=True)
    ecsa_payment_revision = models.BooleanField(null=True, blank=True)
    ecsa_former_member = models.BooleanField(null=True, blank=True)
    ecsa_member_number = models.IntegerField(null=True, blank=True)

    lastname = models.CharField(_("Last name"), max_length=50, blank=True, null=True)
    ecsa_reduced_fee = models.BooleanField(_("Reduced fee"), default=False)
    ecsa_old_member_fee = models.BooleanField(_("20% discount for CSA/ACSA members"), default=False)
    street = models.CharField(_("Street"), max_length=50, blank=True, null=True)
    postal_code = models.IntegerField(null=True, blank=True)
    city = models.CharField(_("City"), max_length=50, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=50, blank=True, null=True)
    occupation = models.ForeignKey(OrganisationType, null=True, blank=True, on_delete=models.CASCADE)

    def admin_send_welcome_email(self): 
        return format_html('<input type="submit" value="Send welcome email" name="_continue">')
    admin_send_welcome_email.allow_tags = True
    admin_send_welcome_email.short_description = "Welcome email"


    class Meta:
        abstract = True


@python_2_unicode_compatible
class Profile(BaseProfile):
    def __str__(self):
        return "{}'s profile".format(self.user)
