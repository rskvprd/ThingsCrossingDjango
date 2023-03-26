from rest_framework import serializers

import ThingsCrossing.models as models


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Characteristic
        fields = ("name", "value")


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Price
        fields = ("value", "currency_code")


class PicturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Picture
        fields = ("image_url",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ("category",)


class AdvertisementSerializer(serializers.ModelSerializer):
    image_urls = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="image_url",
        allow_null=True
    )
    prices = PriceSerializer(many=True)
    characteristics = CharacteristicSerializer(many=True)
    categories = CategorySerializer(many=True)

    class Meta:
        model = models.Advertisement
        fields = "__all__"
