from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings

class Station(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length = 100)
    code = models.CharField(max_length = 10)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length = 100)
    number = models.IntegerField()

    def __str__(self):
        return self.name

class Route(models.Model):
    tid = models.ForeignKey(Train, on_delete = models.CASCADE)
    sid = models.ForeignKey(Station, on_delete = models.CASCADE)
    serial_no = models.IntegerField()
