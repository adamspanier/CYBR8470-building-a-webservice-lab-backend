#from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import *
from django.contrib.auth import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django_filters.rest_framework import DjangoFilterBackend


from django.shortcuts import *

# Import models
from django.db import models
from django.contrib.auth.models import *
from api.models import *

#REST API
from rest_framework import viewsets, filters, parsers, renderers
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import *
from rest_framework.decorators import *
from rest_framework.authentication import *

#filters
#from filters.mixins import *

from api.pagination import *
import json, datetime, pytz
from django.core import serializers
from . import serializers as szs
import requests
import re


def home(request):
   """
   Send requests to / to the ember.js clientside app
   """
   return render_to_response('ember/index.html',
               {}, RequestContext(request))

def xss_example(request):
  """
  Send requests to xss-example/ to the insecure client app
  """
  return render_to_response('dumb-test-app/index.html',
              {}, RequestContext(request))

class Register(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username') #you need to apply validators to these
        print username
        password = request.POST.get('password') #you need to apply validators to these
        email = request.POST.get('email') #you need to apply validators to these
        gender = request.POST.get('gender') #you need to apply validators to these
        age = request.POST.get('age') #you need to apply validators to these
        educationlevel = request.POST.get('educationlevel') #you need to apply validators to these
        city = request.POST.get('city') #you need to apply validators to these
        state = request.POST.get('state') #you need to apply validators to these

        print request.POST.get('username')
        if User.objects.filter(username=username).exists():
            return Response({'username': 'Username is taken.', 'status': 'error'})
        elif User.objects.filter(email=email).exists():
            return Response({'email': 'Email is taken.', 'status': 'error'})

        #especially before you pass them in here
        newuser = User.objects.create_user(email=email, username=username, password=password)
        newprofile = Profile(user=newuser, gender=gender, age=age, educationlevel=educationlevel, city=city, state=state)
        newprofile.save()

        return Response({'status': 'success', 'userid': newuser.id, 'profile': newprofile.id})

class Session(APIView):
    permission_classes = (AllowAny,)
    def form_response(self, isauthenticated, userid, username, error=""):
        data = {
            'isauthenticated': isauthenticated,
            'userid': userid,
            'username': username
        }
        if error:
            data['message'] = error

        return Response(data)

    def get(self, request, *args, **kwargs):
        # Get the current user
        if request.user.is_authenticated():
            return self.form_response(True, request.user.id, request.user.username)
        return self.form_response(False, None, None)

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return self.form_response(True, user.id, user.username)
            return self.form_response(False, None, None, "Account is suspended")
        return self.form_response(False, None, None, "Invalid username or password")

    def delete(self, request, *args, **kwargs):
        # Logout
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class Events(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get(self, request, format=None):
        events = Event.objects.all()
        json_data = serializers.serialize('json', events)
        content = {'events': json_data}
        return HttpResponse(json_data, content_type='json')

    def post(self, request, *args, **kwargs):
        print 'REQUEST DATA'
        print str(request.data)

        eventtype = request.data.get('eventtype')
        timestamp = int(request.data.get('timestamp'))
        userid = request.data.get('userid')
        requestor = request.META['REMOTE_ADDR']

        newEvent = Event(
            eventtype=eventtype,
            timestamp=datetime.datetime.fromtimestamp(timestamp/1000, pytz.utc),
            userid=userid,
            requestor=requestor
        )

        try:
            newEvent.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newEvent.save()
        print 'New Event Logged from: ' + requestor
        return Response({'success': True}, status=status.HTTP_200_OK)


# Not Authenticated
# Should require Auth since we're digesting and exposing data
# No type check, it just converts it to a string
# This is not a parameterized request
# No restrictions on who can access the data
class ActivateIFTTT(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def post(self,request):
        print 'REQUEST DATA!!!'
        print str(request.data)

        eventtype = str(request.data.get('eventtype'))
        sanitized_eventtype = re.sub(r'[^a-zA-Z0-9]', '', eventtype)
        timestamp = int(request.data.get('timestamp'))
        requestor = str(request.META['REMOTE_ADDR'])
        sanitized_requestor = re.sub(r'[^a-zA-Z0-9]', '', requestor)
        api_key = ApiKey.objects.all().first()
        event_hook = "test"

        print(sanitized_eventtype, sanitized_requestor)

        print "Creating New event"

        newEvent = Event(
            eventtype=sanitized_eventtype,
            timestamp=datetime.datetime.fromtimestamp(timestamp/1000, pytz.utc),
            userid=str(api_key.owner),
            requestor=sanitized_requestor
        )

        print newEvent
        print "Sending Device Event to IFTTT hook: " + str(event_hook)

        #send the new event to IFTTT and print the result
        event_req = requests.post('https://maker.ifttt.com/trigger/'+str(event_hook)+'/with/key/'+api_key.key, data= {
            'value1' : timestamp,
            'value2':  "\""+str(eventtype)+"\"",
            'value3' : "\""+str(requestor)+"\""
        })
        print event_req.text

        #check that the event is safe to store in the databse
        try:
            newEvent.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        #log the event in the DB
        newEvent.save()
        print 'New Event Logged'
        return Response({'success': True}, status=status.HTTP_200_OK)

class DogList(APIView):
    """
    Present a list of all Dogs
    """
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get(self, request, format=None):
        dog = Dog.objects.all()
        json_dogs = serializers.serialize('json', dog)
        content = {'dogs': json_dogs}
        return HttpResponse(json_dogs, content_type='json')

    def post(self, request, *args, **kwargs):
        print 'Get DATA'
        print str(request.data)

        name = request.data.get('name')
        age = int(request.data.get('age'))
        breed = request.data.get('breed')
        gender = request.data.get('gender')
        color = request.data.get('color')
        favoritefood = request.data.get('favoritefood')
        favoritetoy = request.data.get('favoritetoy')

        newdog = Dog(
            name = name,
            age = age,
            breed = breed,
            gender = gender,
            color = color,
            favoritefood = favoritefood,
            favoritetoy = favoritetoy
        )

        try:
            newdog.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newdog.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

class DogDetail(APIView):
    """
    Retreive details relating to a specific Dog
    """

    def get(self, request, id):
        print(id)
        dog = Dog.objects.get(pk=id)
        print(dog)
        json_dog = serializers.serialize('json', [dog])
        content = {'dogs': json_dog}
        return HttpResponse(json_dog, content_type='json')

    #here
    #Tyring to get the put method working to put
    #Catching the exception, but not actually putting anything
    def put(self, request, id):
        try:
            dog = Dog.objects.get(pk=id)
            # This is the replacement data
            print(request.data)

            name = request.data.get('name')
            age = int(request.data.get('age'))
            breed = request.data.get('breed')
            gender = request.data.get('gender')
            color = request.data.get('color')
            favoritefood = request.data.get('favoritefood')
            favoritetoy = request.data.get('favoritetoy')

            newdog = Dog(
                id=id,
                name = name,
                age = age,
                breed = breed,
                gender = gender,
                color = color,
                favoritefood = favoritefood,
                favoritetoy = favoritetoy
            )

            json_dog = serializers.serialize('json', [dog])
            # This is the existing data
            print(newdog)
            newdog.save(id)
            return Response(json_dog.data)
        except BaseException as err:
            print(err)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        dog = Dog.objects.get(pk=id)
        dog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BreedList(APIView):
    """
    Present a list of all Dogs
    """
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get(self, request, format=None):
        breed = Breed.objects.all()
        json_breeds = serializers.serialize('json', breed)
        content = {'breeds': json_breeds}
        return HttpResponse(json_breeds, content_type='json')

    def post(self, request, *args, **kwargs):
        print 'Get DATA'
        print str(request.data)

        name = request.data.get('name')
        size = request.data.get('size')
        friendliness = request.data.get('friendliness')
        trainability = request.data.get('trainability')
        sheddingamount = request.data.get('sheddingamount')
        exersciseneeds = request.data.get('exersciseneeds')

        newbreed = Breed(
            id=id,
            name = name,
            size = size,
            friendliness = friendliness,
            trainability = trainability,
            sheddingamount = sheddingamount,
            exersciseneeds = exersciseneeds
        )

        try:
            newbreed.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newbreed.save()
        return Response({'success': True}, status=status.HTTP_200_OK)


class BreedDetail(APIView):
    """
    Retreive details relating to a specific Dog
    """

    def get(self, request, id):
        print(id)
        breed = Breed.objects.get(pk=id)
        print(breed)
        json_breed = serializers.serialize('json', [breed])
        content = {'dogs': json_breed}
        return HttpResponse(json_breed, content_type='json')

    #here
    #Tyring to get the put method working to put
    #Catching the exception, but not actually putting anything
    def put(self, request, id):
        try:
            breed = Breed.objects.get(pk=id)
            # This is the replacement data
            print(request.data)

            name = request.data.get('name')
            size = request.data.get('size')
            friendliness = request.data.get('friendliness')
            trainability = request.data.get('trainability')
            sheddingamount = request.data.get('sheddingamount')
            exersciseneeds = request.data.get('exersciseneeds')

            newbreed = Breed(
                id=id,
                name = name,
                size = size,
                friendliness = friendliness,
                trainability = trainability,
                sheddingamount = sheddingamount,
                exersciseneeds = exersciseneeds
            )

            json_breed = serializers.serialize('json', [breed])
            # This is the existing data
            print(newbreed)
            newbreed.save(id)
            return Response(json_breed.data)
        except BaseException as err:
            print(err)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        breed = Breed.objects.get(pk=id)
        breed.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
