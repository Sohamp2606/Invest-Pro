from django.db import models



class tickerslist(models.Model):
    name = models.CharField(max_length=40)
    sysmbol = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"

