from distutils.command import upload
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q


class Advertisement(models.Model):
    in_search = models.BooleanField("Отображать в поиске", default=False)
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
    CURRENCY_CODE_CHOICES = [
        (RU_RUBLE, "Rubles"),
        (US_DOLLAR, "Dollars"),
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

    def __str__(self): return self.category
