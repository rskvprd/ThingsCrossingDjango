from django.shortcuts import render
from rest_framework import viewsets

import ThingsCrossing.models as models
import ThingsCrossing.serializers as serializers


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = models.Advertisement.objects.all()
    serializer_class = serializers.AdvertisementSerializer


class PicturesViewSet(viewsets.ModelViewSet):
    queryset = models.Pictures.objects.all()
    serializer_class = serializers.PicturesSerializer
