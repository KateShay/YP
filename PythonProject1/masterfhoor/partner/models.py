from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
import os


class ProductType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    coefficient = models.FloatField(verbose_name="Коэффициент типа продукции")

    class Meta:
        verbose_name = "Тип продукции"
        verbose_name_plural = "Типы продукции"

    def __str__(self):
        return self.name


class MaterialType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    defect_percentage = models.FloatField(verbose_name="Процент брака")

    class Meta:
        verbose_name = "Тип материала"
        verbose_name_plural = "Типы материалов"

    def __str__(self):
        return self.name


class Material(models.Model):
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, verbose_name="Тип материала")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    unit = models.CharField(max_length=50, verbose_name="Единица измерения")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    stock = models.IntegerField(verbose_name="Остатки")
    min_stock = models.IntegerField(verbose_name="Минимальный остаток")

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.name


class Product(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, verbose_name="Тип продукции")
    article = models.CharField(max_length=100, unique=True, verbose_name="Артикул")
    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True)
    min_partner_cost = models.DecimalField(max_digits=10, decimal_places=2,
                                           verbose_name="Минимальная стоимость для партнера")

    class Meta:
        verbose_name = "Продукция"
        verbose_name_plural = "Продукция"

    def __str__(self):
        return f"{self.article} - {self.name}"


class PartnerType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")

    class Meta:
        verbose_name = "Тип партнера"
        verbose_name_plural = "Типы партнеров"

    def __str__(self):
        return self.name


class Partner(models.Model):
    partner_type = models.ForeignKey(PartnerType, on_delete=models.CASCADE, verbose_name="Тип партнера")
    name = models.CharField(max_length=255, verbose_name="Наименование компании")
    rating = models.IntegerField(
        verbose_name="Рейтинг",
        validators=[MinValueValidator(0)]
    )
    address = models.TextField(verbose_name="Юридический адрес")
    director_name = models.CharField(max_length=255, verbose_name="ФИО директора")

    phone_regex = RegexValidator(
        regex=r'^\+7\d{10}$',
        message="Телефон должен быть в формате: '+79999999999'."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=12,
        verbose_name="Телефон"
    )

    email = models.EmailField(verbose_name="Email")
    inn = models.CharField(max_length=12, verbose_name="ИНН", blank=True)
    logo = models.ImageField(upload_to='partner_logos/', verbose_name="Логотип", blank=True)

    class Meta:
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"
        ordering = ['-rating', 'name']

    def __str__(self):
        return self.name

    def calculate_discount(self):
        total_sales = SalesHistory.objects.filter(partner=self).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

        if total_sales > 300000:
            return 15
        elif total_sales > 50000:
            return 10
        elif total_sales > 10000:
            return 5
        else:
            return 0


class SalesHistory(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, verbose_name="Партнер")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукция")
    quantity = models.IntegerField(verbose_name="Количество", validators=[MinValueValidator(1)])
    sale_date = models.DateField(verbose_name="Дата продажи")

    class Meta:
        verbose_name = "История реализации"
        verbose_name_plural = "История реализации"
        ordering = ['-sale_date']

    def __str__(self):
        return f"{self.partner.name} - {self.product.name} - {self.sale_date}"


class Recipe(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукция")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="Материал")
    material_quantity = models.FloatField(verbose_name="Количество материала")

    class Meta:
        verbose_name = "Рецептура"
        verbose_name_plural = "Рецептура"
        unique_together = ['product', 'material']

    def __str__(self):
        return f"{self.product.name} - {self.material.name}"


def calculate_material_required(product_type_id, material_type_id, product_quantity, param1, param2):
    try:
        product_type = ProductType.objects.get(id=product_type_id)
        material_type = MaterialType.objects.get(id=material_type_id)

        if (product_quantity <= 0 or param1 <= 0 or param2 <= 0 or
                not isinstance(product_quantity, int)):
            return -1

        material_per_unit = param1 * param2 * product_type.coefficient

        total_material = material_per_unit * product_quantity

        defect_factor = 1 + (material_type.defect_percentage / 100)
        total_material_with_defect = total_material * defect_factor

        return int(total_material_with_defect) + (1 if total_material_with_defect % 1 > 0 else 0)

    except (ProductType.DoesNotExist, MaterialType.DoesNotExist):
        return -1