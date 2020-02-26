from django.db import models
from django.conf import settings


class Keyword(models.Model):
    keyword = models.TextField()
    def __str__(self):        
        return f'{self.keyword}'

class Category(models.Model):
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        res = str(self.text) 
        if(self.parent):
            res  +=  ' - ' + str(self.parent)
        return res

class Resource(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    about  = models.CharField(max_length=200)
    abstract = models.CharField(max_length=300)
    aggregateRating = models.CharField(max_length=100)
    audience = models.CharField(max_length=100)
    datePublished = models.DateTimeField('Date Published')
    inLanguage = models.CharField(max_length=100)
    keywords = models.ManyToManyField(Keyword)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    license =  models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)

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