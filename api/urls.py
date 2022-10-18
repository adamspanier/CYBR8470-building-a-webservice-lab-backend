from django.conf.urls import include, url

#Django Rest Framework
from rest_framework import routers
from . import views
from api import controllers
from django.views.decorators.csrf import csrf_exempt

#REST API routes
router = routers.DefaultRouter()

urlpatterns = [
    url(r'^session', csrf_exempt(controllers.Session.as_view())),
    url(r'^register', csrf_exempt(controllers.Register.as_view())),
    url(r'^events', csrf_exempt(controllers.Events.as_view())),
    url(r'dogs$', controllers.DogList.as_view()),
    url(r'dogs/(?P<id>[0-9]+)$', controllers.DogDetail.as_view()),
    url(r'breeds$', controllers.BreedList.as_view()),
    url(r'breeds/(?P<id>[0-9]+)$', controllers.BreedDetail.as_view()),
    url(r'^activateifttt', csrf_exempt(controllers.ActivateIFTTT.as_view())),
    url(r'^', include(router.urls))
]
