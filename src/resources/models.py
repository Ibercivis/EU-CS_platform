from django.db import models
from django.conf import settings
from authors.models import Author
from organisations.models import Organisation
from projects.models import Project


class Keyword(models.Model):
    keyword = models.TextField()

    def __str__(self):
        return f'{self.keyword}'


class Theme(models.Model):
    theme = models.TextField()

    def __str__(self):
        return f'{self.theme}'


class Audience(models.Model):
    audience = models.TextField()

    def __str__(self):
        return f'{self.audience}'


class Category(models.Model):
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        res = str(self.text)
        if(self.parent):
            res = str(self.parent) + ' : ' + res
        return res


class EducationLevel(models.Model):
    educationLevel = models.TextField()

    def __str__(self):
        return f'{self.educationLevel}'


class LearningResourceType(models.Model):
    learningResourceType = models.TextField()

    def __str__(self):
        return f'{self.learningResourceType}'


class Resource(models.Model):

    creator = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE)

    # Main information, mandatory
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    keywords = models.ManyToManyField(Keyword)
    abstract = models.CharField(max_length=3000)
    description_citizen_science_aspects = models.CharField(max_length=2000)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    audience = models.ManyToManyField(Audience)
    theme = models.ManyToManyField(Theme)

    # Publish information
    # TODO: Convert datePublished to Year
    authors = models.ManyToManyField(Author)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    datePublished = models.IntegerField(null=True, blank=True)
    resourceDOI = models.CharField(max_length=100, null=True, blank=True)
    inLanguage = models.CharField(max_length=100)
    license = models.CharField(max_length=300, null=True, blank=True)

    # Links
    organisation = models.ManyToManyField(Organisation)
    project = models.ManyToManyField(Project)

    # Pictures
    image1 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit1 = models.CharField(max_length=300, null=True, blank=True)
    image2 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit2 = models.CharField(max_length=300, null=True, blank=True)

    # Training resources fields
    isTrainingResource = models.BooleanField(null=True, blank=True)
    educationLevel = models.ManyToManyField(EducationLevel)
    learningResourceType = models.ManyToManyField(LearningResourceType)
    timeRequired = models.FloatField(null=True, blank=True)
    conditionsOfAccess = models.CharField(max_length=300, null=True, blank=True)

    # Time
    # Legacy TODO: delete dateUploaded
    dateUploaded = models.DateTimeField('Date Uploaded')
    dateCreated = models.DateTimeField('Created date', auto_now_add=True)
    dateUpdated = models.DateTimeField('Updated date', auto_now=True)

    # Moderation
    moderated = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    # Other
    hidden = models.BooleanField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    own = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.name


class ResourceGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ResourcesGrouped(models.Model):
    group = models.ForeignKey(ResourceGroup, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("group", "resource"),)

    def __str__(self):
        return str(self.group) + ' - ' + str(self.resource)


class ApprovedResources(models.Model):
    resource = models.OneToOneField(Resource, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.resource}'


class UnApprovedResources(models.Model):
    resource = models.OneToOneField(Resource, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.resource}'

# TODO: Important! copy SavedResources table to Bookmarked resources


class BookmarkedResources(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'resource'),)

    def __str__(self):
        return f'{self.resource} - {self.user.name}'


class SavedResources(models.Model):
    class Meta:
        unique_together = (('user', 'resource'),)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.resource} - {self.user.name}'


class ResourcePermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
