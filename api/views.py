from django.shortcuts import render
from django.http import HttpResponse
from . import models
from datetime import date
from rest_framework import viewsets
from rest_framework import serializers
from django.contrib.auth.models import User
from . import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
import json, datetime, pytz
import requests
from rest_framework import viewsets, filters, parsers, renderers

# Create your views here.

class DogDetail(APIView):
    """
    Retreive details relating to a specific Dog
    """

    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get(self, request, *args, **kwargs):
        queryset = self.get_object(pk)
        serializer = serializers.DogSerializer(queryset)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        dog = self.get_object(pk)
        serializer = serializers.DogSerializer(dog, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk, request):
        dog = self.get_object(pk)
        dog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DogList(APIView):
    """
    Present a list of all Dogs
    """

#    def get(self, request):
#        dogs = models.Dog.objects.all()
#        serializer = serializers.DogSerializer(dogs, many=True)
#        return Response(serializer.data)
#
#    def post(self, request, *args, **kwargs):
#        pass
#        serializer = serializers.DogSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BreedDetail(APIView):
    """
    Retreive details relating to a specific Breed
    """
    def get(self, pk, request):
        breed = self.get_object(pk)
        serializer = serializers.BreedSerializer(breed)
        return Response(serializer.data)

    def put(self, pk, request):
        breed = self.get_object(pk)
        serializer = serializers.BreedSerializer(breed, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, pk, request):
        breed = self.get_object(pk)
        breed.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BreedList(APIView):
    """
    Present a list of all Breeds
    """
    def get(self, request):
        breeds = models.Breed.objects.all()
        serializer = serializers.BreedSerializer(breeds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.BreedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
