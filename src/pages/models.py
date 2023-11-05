from django.db import models
from django.conf import settings


# Create your models here.

class Pages(models.Model):
    creator =  creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Pages"
        ordering = ["-created_on"]

    def __str__(self):
        return self.name


