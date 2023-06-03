import datetime

from django.http import HttpResponse
from pytz import UTC
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
    def my(self, request):
        user: models.User = request.user
        if user.is_anonymous:
            return HttpResponse('Unauthorized', status=401)
        user_profile = models.UserProfile.objects.get(user=user)
        advertisements = models.Advertisement.objects.filter(user_profile=user_profile).order_by('updated_at')
        return Response(serializers.AdvertisementSerializer(advertisements, many=True).data)

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

        serializer = self.get_serializer(sorted_advertisement, many=True)
        data = serializer.data
        if sort_by == "price":
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

    def create(self, request, *args, **kwargs):
        room_id = request.data["room"]
        room = models.Room.objects.get(pk=room_id)

        text = request.data["text"]

        from_user = models.UserProfile.objects.get(user=request.user)

        message = models.Message.objects.create(from_user=from_user, room=room, text=text)

        room.last_message = message
        room.save()

        message_serializer = serializers.MessageSerializer(message)

        return Response(message_serializer.data)

    @action(methods=['post'], detail=False, url_path="by-room")
    def by_room(self, request):
        room = request.data
        messages = models.Message.objects.filter(room=room)
        messages_serializer = serializers.MessageSerializer(
            messages, many=True)
        return Response(messages_serializer.data)

    @action(methods=['post'], detail=False)
    def with_user(self, request):
        from_user = models.UserProfile.objects.get(user=request.user)
        to_user = json.loads(request.body)["to_user"]

        messages = self.queryset.filter(from_user=from_user, to_user=to_user)

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        current_user = request.user
        current_user_profile = models.UserProfile.objects.get(
            user=current_user)
        rooms = self.get_rooms_by_user_profile(current_user_profile)
        serialized_rooms = serializers.RoomSerializer(rooms, many=True)

        return Response(serialized_rooms.data)

    """Get or create private room with two users"""

    @action(methods=['post'], detail=False)
    def private(self, request):
        me = models.UserProfile.objects.get(
            user=request.user)

        companion_id = request.data["companion_id"]
        companion = models.UserProfile.objects.get(pk=companion_id)

        room = self.find_private_room(me, companion)

        if room:
            return Response(serializers.RoomSerializer(instance=room).data)

        room = models.Room.objects.create(type="private")

        models.Participant.objects.create(room=room, participant=companion)
        models.Participant.objects.create(room=room, participant=me)

        return Response(serializers.RoomSerializer(instance=room).data)

    def find_private_room(self, user: models.UserProfile, other_user: models.UserProfile) -> models.Room | None:
        user_rooms = set(self.get_rooms_by_user_profile(user))
        other_user_rooms = set(self.get_rooms_by_user_profile(other_user))

        mutual_room = list(filter(lambda r: r.type == "private", user_rooms & other_user_rooms))
        assert len(mutual_room) <= 1, """There's can't be more than one private room between 2 users"""

        return mutual_room[0] if mutual_room else None

    def get_rooms_by_user_profile(self, user_profile: models.UserProfile):
        my_participants = models.Participant.objects.filter(
            participant=user_profile)
        rooms = sorted(map(lambda p: p.room, my_participants),
                       key=lambda x:
                       x.last_message.sent_date_time.replace(tzinfo=UTC)
                       if x.last_message else datetime.datetime.min.replace(tzinfo=UTC), reverse=True)
        return rooms
