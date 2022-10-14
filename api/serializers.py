# Serializers live here

from rest_framework import serializers
from . import models

class DogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Dog
        fields = ['name', 'age', 'gender', 'color', 'favoritefood', 'favoritetoy']

class BreedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Breed
        fields = ['name', 'size', 'friendliness', 'trainability', 'sheddingamount', 'exersciseneeds']
