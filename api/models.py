from __future__ import unicode_literals

from django.db import models
from django.core.validators import *

from django.contrib.auth.models import User, Group

from django.contrib import admin
import base64
import re

class Event(models.Model):
    eventtype = models.CharField(max_length=1000, blank=False)
    timestamp = models.DateTimeField()
    userid = models.CharField(max_length=1000, blank=True)
    requestor = models.GenericIPAddressField(blank=False)

    def __str__(self):
        desc = str(self.eventtype)
        san_desc = re.sub(r'a-zA-Z0-9', '', desc)
        return san_desc

class EventAdmin(admin.ModelAdmin):
    list_display = ('eventtype', 'timestamp')

class ApiKey(models.Model):
    owner = models.CharField(max_length=1000, blank=False)
    key = models.CharField(max_length=5000, blank=False)

    def __str__(self):
        return str(self.owner) + str(self.key)

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('owner','key')

# Create a model for dog
class Dog(models.Model):
    name = models.CharField(max_length=40, unique=True)
    age = models.IntegerField()
    breed = models.ForeignKey("Breed", on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    color = models.CharField(max_length=10)
    favoritefood = models.CharField(max_length=20)
    favoritetoy = models.CharField(max_length=20)

    def __str__(self):
        return (self.name) + ": " + (self.breed.name) + ": " + (self.color)

    class DogAdmin(admin.ModelAdmin):
        fields = ('name', 'age', 'breed', 'gender', 'color', 'favoritefood', 'favoritetoy')
        list_display = ('name', 'age', 'breed', 'gender', 'color', 'favoritefood', 'favoritetoy')

admin.site.register(Dog, Dog.DogAdmin)

#Size array for breed size
SIZES = [
    ("Tiny", "Tiny"),
    ("Small", "Small"),
    ("Medium", "Medium"),
    ("Large", "Large"),
]

# Create a model for breed
class Breed(models.Model):
    name = models.CharField(max_length=40, unique=True)
    size = models.CharField(max_length=10, choices=SIZES)
    friendliness = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    trainability = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    sheddingamount = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    exersciseneeds = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])

    def __str__(self):
        return (self.name) + ": " + (self.size)

    class BreedAdmin(admin.ModelAdmin):
        fields = ('name', 'size', 'friendliness', 'trainability', 'sheddingamount', 'exersciseneeds')
        list_display = ('name', 'size', 'friendliness', 'trainability', 'sheddingamount', 'exersciseneeds')

admin.site.register(Breed, Breed.BreedAdmin)
