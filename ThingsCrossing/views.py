from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.forms.models import model_to_dict

from django.shortcuts import get_object_or_404

import json
import ThingsCrossing.models as models
import ThingsCrossing.serializers as serializers


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = models.Advertisement.objects.all()
    serializer_class = serializers.AdvertisementSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        sort_by = self.request.query_params.get("sort-by")
        is_ascending = self.request.query_params.get("is-ascending")

        is_ascending = is_ascending == "true"

        searched_advertisement = models.Advertisement.objects.filter(
            title__contains=search_value, in_search=True)

        sorted_advertisement = None

        if sort_by == "title":
            if is_ascending:
                sorted_advertisement = searched_advertisement.order_by("title")
            else:
                sorted_advertisement = searched_advertisement.order_by(
                    "-title")
        elif sort_by == "price":
            if is_ascending:
                sorted_advertisement = searched_advertisement
            else:
                sorted_advertisement = searched_advertisement
        else:
            if is_ascending:
                sorted_advertisement = searched_advertisement.order_by(
                    "updated_at")
            else:
                sorted_advertisement = searched_advertisement.order_by(
                    "-updated_at")

        print(f"{sort_by=} {is_ascending=} {search_value=}", )
        print(f"{sorted_advertisement=}")

        serializer = self.get_serializer(sorted_advertisement, many=True)
        data = serializer.data
        if sort_by == "price":
            print([data[i]['prices'][0] if data[i]['prices']
                  else None for i in range(len(data))])
            if is_ascending:
                data = sorted(
                    data, key=lambda ad: ad['prices'][0]['value'] if ad['prices'] else 0)
            else:
                data = sorted(data, key=lambda ad: -
                              ad['prices'][0]['value'] if ad['prices'] else 0)

        return Response(data)


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
        user_profile = get_object_or_404(models.UserProfile.objects, user=user)
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)


class RegisterUser(generics.CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        user_serializer: serializers.UserSerializer = self.get_serializer(
            data=request.data)
        user_serializer.is_valid(raise_exception=True)
        self.perform_create(user_serializer)
        user: models.User = user_serializer.instance
        token = Token.objects.create(user=user)

        profile = models.UserProfile.objects.create(user=user)

        profile_serializer = serializers.UserProfileSerializer(profile)

        response_data = {
            'user': user_serializer.data,
            'token': token.key,
            'profile': profile_serializer.data,
        }
        return Response(response_data)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['post'], detail=False)
    def with_user(self, request):
        from_user = models.UserProfile.objects.get(user=request.user)
        to_user = json.loads(request.body)["to_user"]

        messages = self.queryset.filter(from_user=from_user, to_user=to_user)

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
