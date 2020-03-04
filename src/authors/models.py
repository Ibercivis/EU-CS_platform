from django.db import models

class Author(models.Model):
    author = models.TextField()
    def __str__(self):        
        return f'{self.author}'