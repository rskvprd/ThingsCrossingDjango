from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.shortcuts import get_object_or_404

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
            image_model = models.Picture.objects.get(image=relative_image_url)
            image_model.advertisement_id = advertisement_id
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


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer

    @action(detail=False, methods=['post'], url_path="get-by-token")
    def get_by_token(self, request):
        token = json.loads(request.body)['token']

        user = get_object_or_404(Token.objects, key=token).user
        print(f'{user=}')
        user_profile = get_object_or_404(models.UserProfile.objects, user=user)
        print(f'{user_profile=}')
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)


class RegisterUser(generics.CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        user_serializer: serializers.UserSerializer = self.get_serializer(
            data=request.data)
        user_serializer.is_valid(raise_exception=True)
        self.perform_create(user_serializer)
        user: models.User = user_serializer.instance
        token = Token.objects.create(user=user)

        profile = models.UserProfile.objects.create(user=user)
        profile_serializer = serializers.UserProfileSerializer(
            instance=profile)

        response_data = {
            'user': user_serializer.data,
            'token': token.key,
            'profile': profile_serializer.data,
        }
        return Response(response_data)
