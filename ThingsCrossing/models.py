from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q
from django.contrib.auth.models import User


class Advertisement(models.Model):
    in_search = models.BooleanField("Show in search", default=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=5000)
    address = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_profile = models.ForeignKey(
        to="UserProfile",
        on_delete=models.CASCADE,
        related_name="user_profile"
    )

    def __str__(self): return self.title


class Characteristic(models.Model):
    """
    TODO: Сделать таблицы Category, CharacteristicCategory, CharacteristicName, CharacteristicValues
        В которых будут храниться категории товаров, характеристики, подходящие к соответствующим
        категориям товаров, и значения, подходящие к соответсвующей характеристике.
    """
    value = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    advertisement = models.ForeignKey(
        to='Advertisement',
        on_delete=models.CASCADE,
        related_name="characteristics"
    )

    def __str__(self): return f'{self.name}: {self.value}'


class Picture(models.Model):
    advertisement = models.ForeignKey(
        to="Advertisement",
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
    )
    image = models.ImageField(
        verbose_name="Картинки",
        upload_to="advertisement_pictures",
    )

    def __str__(self): return str(self.image)


class Exchange(models.Model):
    """
    TODO: Лучше сделать таблицу ProductModel со списком всевозможных товаров
        и вместо атрибута product_name сделать атрибут product_id, который будет
        ссылаться на ProductModel
    """
    product_name = models.CharField(max_length=255)
    advertisement = models.ForeignKey(
        to='Advertisement',
        on_delete=models.CASCADE,
        related_name="exchanges",
    )

    def __str__(self): return f'{self.product_name} от {self.advertisement}'


class Price(models.Model):
    RU_RUBLE = "RUB"
    US_DOLLAR = "USD"
    KZ_TENGE = "KZT"
    UA_HRYVNIA = "UAH"

    CURRENCY_CODE_CHOICES = [
        (RU_RUBLE, "RU Rubles"),
        (US_DOLLAR, "US Dollars"),
        (KZ_TENGE, "KZ Tenge"),
        (UA_HRYVNIA, "UA Hryvnia"),
    ]
    value = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10 ** 15)])
    currency_code = models.CharField(
        max_length=255, choices=CURRENCY_CODE_CHOICES)
    advertisement = models.ForeignKey(
        to="Advertisement", on_delete=models.CASCADE, related_name="prices")

    def __str__(self):
        return f"{self.advertisement.title}: {self.value} {self.currency_code}"

    class Meta:
        unique_together = (("currency_code", "advertisement"),)
        constraints = (
            CheckConstraint(
                check=Q(value__gte=0.0) & Q(value__lte=10 ** 15),
                name="check_price_value_range",
            ),
        )


class Category(models.Model):
    name = models.CharField(max_length=255)
    advertisement = models.ForeignKey(
        to="Advertisement",
        on_delete=models.CASCADE,
        related_name="categories"
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self): return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        default="profile_picture/default_avatar.jpg", upload_to="profile_picture")

    def __str__(self):
        return self.user.username


class Message(models.Model):
    from_user = models.ForeignKey(
        to=UserProfile,
        on_delete=models.CASCADE,
        related_name="from_user"
    )

    to_user = models.ForeignKey(
        to=UserProfile,
        on_delete=models.CASCADE,
        related_name="to_user",
        null=True,
        blank=True
    )

    room = models.ForeignKey(
        to="Room",
        on_delete=models.CASCADE,
    )
    
    text = models.CharField(max_length=3000)

    sent_date_time = models.DateTimeField(auto_now=True)


class Room(models.Model):
    GROUP = "group"
    PRIVATE = "private"

    TYPE_CHOICES = [
        (GROUP, "Group"),
        (PRIVATE, "Private")
    ]

    type = models.CharField(
        max_length=255,
        choices=TYPE_CHOICES,
        default=PRIVATE
    )
    last_message_datetime = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=True, blank=True)


class Participant(models.Model):
    room = models.ForeignKey(
        to="Room",
        on_delete=models.CASCADE,
        related_name="participants"
    )
    participant = models.ForeignKey(
        to="UserProfile",
        on_delete=models.CASCADE,
        related_name="participant"
    )
