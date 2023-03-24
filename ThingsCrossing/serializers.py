from rest_framework import serializers

import ThingsCrossing.models as models


class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pictures
        fields = "__all__"


class AdvertisementSerializer(serializers.ModelSerializer):
    image_urls = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="image_url",
        allow_null=True
    )

    class Meta:
        model = models.Advertisement
        fields = "__all__"
