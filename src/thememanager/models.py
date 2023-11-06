from django.db import models

# Create your models here.

# A new class to store the top bar
class TopBar(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    position = models.IntegerField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        verbose_name_plural = "TopBar"
        ordering = ["position"]

    def __str__(self):
        return self.name
