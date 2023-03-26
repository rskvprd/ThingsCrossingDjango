from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q


class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=5000)
    address = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.title


class Characteristic(models.Model):
    """
    TODO: Сделать таблицы Category, CharacteristicCategory, CharacteristicName, CharacteristicValues
        В которых будут храниться категории товаров, характеристики, подходящие к соответствующим
        категориям товаров, и значения, подходящие к соответсвующей характеристике.
    """
    value = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    advertisement_id = models.ForeignKey(
        to='Advertisement',
        on_delete=models.CASCADE,
        related_name="characteristics"
    )

    def __str__(self): return f'{self.name}: {self.value}'


class Picture(models.Model):
    """
    TODO: Установить максимальное число картинок, сделать сохранение картинок на свой сервер вместо url
    """
    advertisement_id = models.ForeignKey(
        to="Advertisement",
        on_delete=models.CASCADE,
        related_name="image_urls"
    )
    image_url = models.URLField()

    def __str__(self): return self.image_url


class Exchange(models.Model):
    """
    TODO: Лучше сделать таблицу ProductModel со списком всевозможных товаров
        и вместо атрибута product_name сделать атрибут product_id, который будет
        ссылаться на ProductModel
    """
    product_name = models.CharField(max_length=255)
    advertisement_id = models.ForeignKey(
        to='Advertisement',
        on_delete=models.CASCADE,
        related_name="exchange"
    )

    def __str__(self): return f'{self.product_name} от {self.advertisement_id}'


class Price(models.Model):
    RU_RUBLE = "RUB"
    US_DOLLAR = "USD"
    CURRENCY_CODE_CHOICES = [
        (RU_RUBLE, "Rubles"),
        (US_DOLLAR, "Dollars"),
    ]
    value = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10 ** 15)])
    currency_code = models.CharField(max_length=255, choices=CURRENCY_CODE_CHOICES)
    advertisement_id = models.ForeignKey(to="Advertisement", on_delete=models.CASCADE, related_name="prices")

    def __str__(self):
        return f"{self.advertisement_id.title}: {self.value} {self.currency_code}"

    class Meta:
        unique_together = (("currency_code", "advertisement_id"),)
        constraints = (
            CheckConstraint(
                check=Q(value__gte=0.0) & Q(value__lte=10 ** 15),
                name="check_price_value_range",
            ),
        )


class Category(models.Model):
    category = models.CharField(max_length=255)
    advertisement_id = models.ForeignKey(
        to="Advertisement",
        on_delete=models.CASCADE,
        related_name="categories"
    )

    def __str__(self): return self.category
