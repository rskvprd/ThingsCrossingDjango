from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

import json
import ThingsCrossing.models as models
import ThingsCrossing.serializers as serializers


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = models.Advertisement.objects.all()
    serializer_class = serializers.AdvertisementSerializer

    def create(self, request, *args, **kwargs):
        images = json.loads(request.body)["images"]
        response = super().create(request, *args, **kwargs)
        response.data["images"] = images
        advertisement_id = response.data["id"]
        
        for image in images:
            image_url = image['url']
            relative_image_url = "/".join(image_url.split("/")[4:])
            print(relative_image_url)
            image_model = models.Picture.objects.get(image=relative_image_url)
            image_model.advertisement_id = advertisement_id
            print(image_model.__dict__)
            image_model.save()
        return response

    @action(detail=False, methods=['get'])
    def search(self, request):
        search_value = self.request.query_params.get("q")
        searched_advertisement = models.Advertisement.objects.filter(
            title__contains=search_value, in_search=True)

        serializer = self.get_serializer(searched_advertisement, many=True)
        return Response(serializer.data)


class PicturesViewSet(viewsets.ModelViewSet):
    queryset = models.Picture.objects.all()
    serializer_class = serializers.PictureSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


def form_test(request):
    if request.method == "GET":
        return render(request, "form_test.html")

    request_body = json.loads(request.body)
    print(request_body)
    response = json.dumps({
        "message": "You're succesfully logged in!"
    })
    return HttpResponse(
        response,
    )
