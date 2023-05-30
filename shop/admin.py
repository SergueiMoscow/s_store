from django.contrib import admin

from shop.models import OrderLine, Category, Product, Discount, Order

admin.site.site_header = 'Администрирование магазина "Лариса"'
admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(Discount)
# admin.site.register(Order)
# admin.site.register(OrderLine)


class PriceFilter(admin.SimpleListFilter):
    title = 'Цена'
    parameter_name = 'price'
    round_value = 500

    def lookups(self, request, model_admin):
        """
        return (
            ('100', '0 - 100'),
            ('200', '101 - 200'),
            ('300', '201 - 300'),
            ('400', '301 - 400'),
            ('500', '401 - 500'),
        )

        :param request:
        :param model_admin:
        :return:
        """
        filters = []
        product = Product.objects.order_by('price').last()
        if product:
            # print(product)
            max_price = round(product.price / self.round_value) * self.round_value + self.round_value
            price = self.round_value
            while price <= max_price:
                start = price
                end = f'{price - self.round_value + 1} - {price}'
                filters.append((start, end))
                price += self.round_value
        return filters

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        value = int(self.value())
        return queryset.filter(price__gte=(value - self.round_value+1), price__lte=value)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'image', 'price', 'date')
    # list_filter = ('section', 'price')
    list_filter = ('category', PriceFilter)
    actions_on_bottom = True
    # actions_on_top = False
    list_per_page = 10
    search_fields = ('name',)


class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'value_percent')

    def save_model(self, request, obj, form, change):
        super(DiscountAdmin, self).save_model(request, obj, form, change)


class OrderLineAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'count')
    list_filter = ('order',)


class OrderLinesInline(admin.TabularInline):
    model = OrderLine
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'display_products',
        'display_amount',
        'name',
        'discount',
        'phone',
        'email',
        'address',
        'notice',
        'date_send',
        'status')

    fieldsets = (
        ('Информация о заказе', {
            'fields': ('discount', 'need_delivery')
        }),
        ('Информация о клиенте', {
            'fields': ('name', 'phone', 'email', 'address'),
            'description': 'Контактная информация'
        }),
        ('Доставка и оплата', {
            'fields': ('date_send', 'status')
        }),
    )
    list_filter = ('status', 'date_order')
    date_hierarchy = 'date_order'
    inlines = [OrderLinesInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
# admin.site.register(Order, OrderAdmin)

