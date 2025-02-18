from django.db import models
from django.conf import settings
from authors.models import Author
from organisations.models import Organisation
from projects.models import Project

# TODO: Order this file

class Keyword(models.Model):
    keyword = models.TextField()

    def __str__(self):
        return f'{self.keyword}'


class Theme(models.Model):
    theme = models.CharField(max_length=200)

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
        category_chain = []
        current = self
        max_depth = 10  # Avoid infinite cycles

        while current and max_depth > 0:
            category_chain.append(str(current.text))
            current = current.parent
            max_depth -= 1

        if max_depth == 0:
            category_chain.append("... (loop detected)")  # Indicate detected loop

        return " : ".join(reversed(category_chain))


class EducationLevel(models.Model):
    educationLevel = models.TextField()

    def __str__(self):
        return f'{self.educationLevel}'


class LearningResourceType(models.Model):
    learningResourceType = models.TextField()

    def __str__(self):
        return f'{self.learningResourceType}'
    
class HelpText(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    paragraph = models.TextField()


class Resource(models.Model):

    creator = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE)

    # Main information, mandatory
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    keywords = models.ManyToManyField(Keyword)
    abstract = models.TextField()
    description_citizen_science_aspects = models.TextField()
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    audience = models.ManyToManyField(Audience)
    theme = models.ManyToManyField(Theme)

    # Publish information
    # TODO: Convert datePublished to Year
    authors = models.ManyToManyField(Author, blank=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    datePublished = models.IntegerField(null=True, blank=True)
    resourceDOI = models.CharField(max_length=100, null=True, blank=True)
    inLanguage = models.CharField(max_length=100, blank=True)
    license = models.CharField(max_length=300, null=True, blank=True)

    # Links
    organisation = models.ManyToManyField(Organisation, blank=True)
    project = models.ManyToManyField(Project, blank=True)

    # Pictures
    image1 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit1 = models.CharField(max_length=300, null=True, blank=True)
    image2 = models.ImageField(upload_to='images/', max_length=300, null=True, blank=True)
    imageCredit2 = models.CharField(max_length=300, null=True, blank=True)

    # Training resources fields
    isTrainingResource = models.BooleanField(null=True, blank=True, default=False)
    educationLevel = models.ManyToManyField(EducationLevel, blank=True)
    learningResourceType = models.ManyToManyField(LearningResourceType, blank=True)
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
    featured = models.BooleanField(default=False, blank=True)
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
