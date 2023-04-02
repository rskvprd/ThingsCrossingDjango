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


class PictureSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="image")

    class Meta:
        model = models.Picture
        fields = ("url", "id")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ("name",)


class ExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exchange
        fields = ("product_name",)


class AdvertisementSerializer(serializers.ModelSerializer):
    images = PictureSerializer(many=True)
    prices = PriceSerializer(many=True)
    characteristics = CharacteristicSerializer(many=True)
    categories = CategorySerializer(many=True)
    exchanges = ExchangeSerializer(many=True)

    class Meta:
        model = models.Advertisement
        fields = "__all__"
