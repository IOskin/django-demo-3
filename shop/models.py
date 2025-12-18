from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Производитель")

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Поставщик")

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ("pcs", "шт."),
        ("pack", "уп."),
        ("set", "набор"),
    ]

    name = models.CharField(max_length=200, verbose_name="Наименование товара")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Производитель",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Поставщик",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="pcs",
        verbose_name="Единица измерения",
    )
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="Скидка, %")
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Фото товара",
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def has_discount(self) -> bool:
        return self.discount_percent > 0

    @property
    def final_price(self):
        if not self.has_discount:
            return self.price
        return self.price * (100 - self.discount_percent) / 100

    @property
    def is_out_of_stock(self) -> bool:
        return self.stock_quantity == 0


class UserRole(models.TextChoices):
    GUEST = "guest", "Гость"
    CLIENT = "client", "Клиент"
    MANAGER = "manager", "Менеджер"
    ADMIN = "admin", "Администратор"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        verbose_name="Роль",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:
        return f"{self.full_name} ({self.get_role_display()})"


class Order(models.Model):
    customer = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Клиент",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Заказ #{self.pk} от {self.created_at:%Y-%m-%d}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price_at_order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена на момент заказа",
    )
    discount_percent_at_order = models.PositiveIntegerField(
        default=0, verbose_name="Скидка, % на момент заказа"
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"


