from rest_framework import serializers

import ThingsCrossing.models as models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = models.User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        return user

    class Meta:
        model = models.User
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True}
        }


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


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    avatar = serializers.ImageField(use_url=True)

    class Meta:
        model = models.UserProfile
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ("name",)


class MessageSerializer(serializers.ModelSerializer):
    from_user = UserProfileSerializer(many=False, read_only=True)
    to_user = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = models.Message
        fields = ("__all__")


class ExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exchange
        fields = ("product_name",)


class AdvertisementSerializer(serializers.ModelSerializer):
    images = PictureSerializer(many=True, read_only=True)
    prices = PriceSerializer(many=True)
    characteristics = CharacteristicSerializer(many=True)
    categories = CategorySerializer(many=True)
    exchanges = ExchangeSerializer(many=True)
    user_profile = UserProfileSerializer(many=False, read_only=True)

    def create(self, validated_data):
        prices = validated_data.pop("prices")
        characteristics = validated_data.pop("characteristics")
        categories = validated_data.pop("categories")
        exchanges = validated_data.pop("exchanges")
        profile = models.UserProfile.objects.get(
            user=self.context['request'].user)

        advertisement = models.Advertisement.objects.create(
            **validated_data, user_profile=profile)
        for category in categories:
            models.Category.objects.create(
                advertisement=advertisement, **category)

        for price in prices:
            models.Price.objects.create(advertisement=advertisement, **price)

        for characteristic in characteristics:
            models.Characteristic.objects.create(
                advertisement=advertisement, **characteristic)

        for exchange in exchanges:
            models.Exchange.objects.create(
                advertisement=advertisement, **exchange)

        return advertisement

    def update(self, instance, validated_data):
        prices = set(validated_data.pop("prices", []))
        characteristics = set(validated_data.pop("characteristics", []))
        categories = set(validated_data.pop("categories", []))
        exchanges = set(validated_data.pop("exchanges", []))

        old_prices = set(instance.prices)
        old_characteristics = set(instance.characteristics)
        old_categories = set(instance.categories)
        old_exchanges = set(instance.exchanges)

        removed_prices = old_prices - prices
        removed_characteristics = old_characteristics - characteristics
        removed_categories = old_categories - categories
        removed_exchanges = old_exchanges - exchanges

        # Delete removed records
        for price in removed_prices:
            price.delete()
        for characteristic in removed_characteristics:
            characteristic.delete()
        for category in removed_categories:
            category.delete()
        for exchange in removed_exchanges:
            exchange.delete()

        new_prices = prices - old_prices
        new_characteristics = characteristics - old_characteristics
        new_categories = categories - old_categories
        new_exchanges = exchanges - old_exchanges

        # Add new records
        for price in new_prices:
            models.Price.objects.create(advertisement=instance, **price)
        for category in new_categories:
            models.Category.objects.create(
                advertisement=instance, **categories)
        for characteristic in new_characteristics:
            models.Characteristic.objects.create(
                advertisement=instance, **characteristic)
        for exchange in new_exchanges:
            models.Exchange.objects.create(advertisement=instance, **exchange)

        # Update advertisement
        advertisement = models.Advertisement.objects.filter(pk=instance.id)
        advertisement.update(**validated_data)

        return advertisement.get()

    class Meta:
        model = models.Advertisement
        fields = "__all__"


class ParticipantSerializer(serializers.ModelSerializer):
    participant = UserProfileSerializer()

    class Meta:
        model = models.Participant
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)
    last_message = MessageSerializer(many=False)

    class Meta:
        model = models.Room
        fields = "__all__"
