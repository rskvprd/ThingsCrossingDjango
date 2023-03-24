from django.db import models


class Advertisement(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=5000)
    price = models.IntegerField()
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
    characteristic_value = models.CharField(max_length=255)
    characteristic_name = models.CharField(max_length=255)
    advertisement_id = models.ForeignKey('Advertisement', on_delete=models.CASCADE)

    def __str__(self): return f'{self.characteristic_name}: {self.characteristic_value}'


class Pictures(models.Model):
    """
    TODO: Установить максимальное число картинок, сделать сохранение картинок на свой сервер вместо url
    """
    advertisement_id = models.ForeignKey('Advertisement', on_delete=models.CASCADE, related_name="image_urls")
    image_url = models.URLField()

    def __str__(self): return self.image_url


class Exchange(models.Model):
    """
    TODO: Лучше сделать таблицу ProductModel со списком всевозможных товаров
        и вместо атрибута product_name сделать атрибут product_id, который будет
        ссылаться на ProductModel
    """
    product_name = models.CharField(max_length=255)
    advertisement_id = models.ForeignKey('Advertisement', on_delete=models.CASCADE)

    def __str__(self): return f'{self.product_name} от {self.advertisement_id}'
