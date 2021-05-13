from django.db import models


class Ecsa_fee(models.Model):
    membership = models.TextField()
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.membership}'
