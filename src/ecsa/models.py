from django.db import models
from django.conf import settings

class Ecsa_fee(models.Model):
    membership = models.TextField()
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.membership}'


class InvoiceCounter(models.Model):
    counter = models.IntegerField()
    year = models.IntegerField()


class Delegate(models.Model):
    name = models.TextField()
    email = models.EmailField(unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f'{self.email}'