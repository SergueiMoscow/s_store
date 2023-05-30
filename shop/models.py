import datetime
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(
        max_length=70,
        help_text='Название категории',
        unique=True,
        verbose_name='Название категории'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', args=[self.id])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    name = models.CharField(max_length=70, verbose_name='Название')
    image = models.ImageField(upload_to='images', verbose_name='Изображение')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    weight = models.IntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(10000)],
        default=0
    )
    description = models.TextField(verbose_name='Описание')
    date = models.DateField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Тоавр'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return '{0}-({1})'.format(self.name, self.category.name)


class Discount(models.Model):
    code = models.CharField(max_length=10, verbose_name='Код купона')
    value = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='В процентах'
    )

    class Meta:
        ordering = ['-value']
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        return f'{self.code}({str(self.value)}%)'

    def value_percent(self):
        return f'{self.value}%'

    value_percent.short_description = 'Размер скидки '


class Order(models.Model):
    need_delivery = models.BooleanField(verbose_name='Необходимость доставки')
    discount = models.ForeignKey(Discount, verbose_name='Скидка', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name='Имя')
    phone = models.CharField(max_length=50, verbose_name='Телефон')
    email = models.EmailField()
    address = models.CharField(max_length=100, verbose_name='Адрес', blank=True)
    notice = models.CharField(max_length=150, blank=True, null=True, verbose_name='Примечания к заказу')
    date_order = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    date_send = models.DateTimeField(blank=True, null=True, verbose_name='Дата отправки')

    STATUSES = [
        ('NEW', 'Новый заказ'),
        ('APR', 'Подтверждён'),
        ('PAY', 'Оплачен'),
        ('CNL', 'Отменён')
    ]

    status = models.CharField(choices=STATUSES, max_length=3, verbose_name='Статус', default='NEW')

    class Meta:
        ordering = ['-date_order']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'ID: {str(self.id)}'

    def display_products(self):
        display = ''
        for order_line in self.orderline_set.all():
            display += f'{order_line.product.name}: {order_line.count} шт.\n'
        return display

    def display_amount(self):
        amount = Decimal(0.0)
        for order_line in self.orderline_set.all():
            amount += order_line.price * order_line.count
        if self.discount:
            amount = round(amount * Decimal(1 - self.discount.value / 100))
        return f'{amount} руб.'

    display_products.short_description = 'Состав заказа'
    display_amount.short_description = 'Сумма'


class OrderLine(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    count = models.IntegerField(verbose_name='Количество', validators=[MinValueValidator(1)], default=1)

    class Meta:
        verbose_name = 'Строка заказа'
        verbose_name_plural = 'Строки заказа'

    def __str__(self):
        return 'Заказ (ID {0}) {1}, {2} шт.'.format(self.order.id, self.product.name, self.count)




