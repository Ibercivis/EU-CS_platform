from django.db import models
from django.conf import settings


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
            res  +=  ' - ' + str(self.parent)
        return res

class Resource(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_rsc =  models.CharField(max_length=100)
    author_email =  models.CharField(max_length=100)
    abstract = models.CharField(max_length=1000)
    aggregateRating = models.CharField(max_length=100)
    audience = models.ForeignKey(Audience, null=True, blank=True, on_delete=models.CASCADE)
    dateUploaded = models.DateTimeField('Date Uploaded')
    inLanguage = models.CharField(max_length=100)
    keywords = models.ManyToManyField(Keyword)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    license =  models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    datePublished = models.IntegerField()
    theme = models.ManyToManyField(Theme)
    imageURL = models.CharField(max_length=200)
    resourceDOI = models.CharField(max_length=100)

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


class FeaturedResources(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    def __str__(self):        
        return f'{self.resource}'

class SavedResources(models.Model):
    class Meta:
        unique_together = (('user', 'resource'),)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):        
        return f'{self.resource} - {self.user.name}' 