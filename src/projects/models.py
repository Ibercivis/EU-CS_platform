from django.contrib.gis.db import models
from django.conf import settings
from organisations.models import Organisation


class Status(models.Model):
    status = models.TextField()

    def __str__(self):
        return f'{self.status}'


class Topic(models.Model):
    topic = models.TextField()

    def __str__(self):
        return f'{self.topic}'


class HasTag(models.Model):
    hasTag = models.TextField()

    def __str__(self):
        return f'{self.hasTag}'


class DifficultyLevel(models.Model):
    difficultyLevel = models.TextField()

    def __str__(self):
        return f'{self.difficultyLevel}'


class ParticipationTask(models.Model):
    participationTask = models.TextField()

    def __str__(self):
        return f'{self.participationTask}'


class GeographicExtend(models.Model):
    geographicextend = models.TextField()

    def __str__(self):
        return f'{self.geographicextend}'


class Keyword(models.Model):
    keyword = models.TextField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.keyword}'


class FundingBody(models.Model):
    body = models.TextField()

    def __str__(self):
        return f'{self.body}'


class OriginDatabase(models.Model):
    originDatabase = models.TextField()

    def __str__(self):
        return f'{self.originDatabase}'


class CustomField(models.Model):
    title = models.TextField()
    paragraph = models.TextField()


# For translation

class TranslatedProject(models.Model):
    translatedDescription = models.CharField(max_length=3000)
    translatedAim = models.CharField(max_length=2000)
    translatedHowToParticipate = models.CharField(max_length=2000)
    translatedEquipment = models.CharField(max_length=2000)
    creator = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE)
    inLanguage = models.TextField(max_length=5)
    dateCreated = models.DateTimeField('Created date', auto_now=True)
    needsUpdate = models.BooleanField(default=False)


class Project(models.Model):
    creator = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE)
    dateCreated = models.DateTimeField('Created date', auto_now_add=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)

    # Main information
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=3000)
    description_citizen_science_aspects = models.CharField(max_length=2000)
    aim = models.CharField(max_length=2000)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword, blank=True)

    # Useful information to classificate the project
    topic = models.ManyToManyField(Topic)
    hasTag = models.ManyToManyField(HasTag)
    start_date = models.DateTimeField('Start date', null=True, blank=True)
    end_date = models.DateTimeField('End date', null=True, blank=True)

    # Participation information
    participationTask = models.ManyToManyField(ParticipationTask)
    difficultyLevel = models.ForeignKey(
            DifficultyLevel,
            default=None,
            blank=True,
            null=True,
            on_delete=models.CASCADE)
    howToParticipate = models.CharField(max_length=2000, null=True, blank=True)
    equipment = models.CharField(max_length=2000, null=True, blank=True)

    # Project Location
    geographicextend = models.ManyToManyField(GeographicExtend, blank=True)
    projectlocality = models.CharField(max_length=300, null=True, blank=True)
    projectGeographicLocation = models.MultiPolygonField(blank=True, null=True)

    # Contact and host details
    author = models.CharField(max_length=100, null=True, blank=True)
    author_email = models.CharField(max_length=100, null=True, blank=True)
    mainOrganisation = models.ForeignKey(
                Organisation,
                on_delete=models.CASCADE,
                null=True,
                blank=True,
                related_name='main_organisation')
    organisation = models.ManyToManyField(Organisation)

    # Funding information
    fundingBody = models.ManyToManyField(FundingBody, blank=True)
    fundingProgram = models.CharField(max_length=500, null=True, blank=True)

    # Images
    image1 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit1 = models.CharField(max_length=300, null=True, blank=True)
    image2 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit2 = models.CharField(max_length=300, null=True, blank=True)
    image3 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit3 = models.CharField(max_length=300, null=True, blank=True)

    # Database information
    origin = models.CharField(max_length=100, null=True, blank=True)
    originDatabase = models.ForeignKey(OriginDatabase, on_delete=models.CASCADE, null=True, blank=True)
    originURL = models.CharField(max_length=200, null=True, blank=True)
    originUID = models.CharField(max_length=200, null=True, blank=True)

    # For moderation
    moderated = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    # Others (some of them not used)
    featured = models.BooleanField(default=False)
    host = models.CharField(max_length=200, null=True, blank=True)
    doingAtHome = models.BooleanField(null=True, default=False)
    participatingInaContest = models.BooleanField(null=True, default=False)
    hidden = models.BooleanField(null=True, blank=True)
    customField = models.ManyToManyField(CustomField, blank=True)

    # For translation
    translatedProject = models.ManyToManyField(TranslatedProject)

    def __str__(self):
        return f'{self.name}'


class ApprovedProjects(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project}'


class UnApprovedProjects(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project}'


class FollowedProjects(models.Model):
    class Meta:
        unique_together = (('user', 'project'),)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project.id}'


class ProjectPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
