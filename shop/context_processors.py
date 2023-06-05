from _decimal import Decimal

from shop.forms import SearchForm
from shop.models import Category, Product, Discount


def add_default_data(request):
    categories = Category.objects.all()
    search_form = SearchForm()
    count_in_cart = 0
    sum_in_cart = 0
    cart_info = request.session.get('cart_info', {})
    for key in cart_info:
        count_in_cart += cart_info[key]
        sum_product = Product.objects.get(pk=key).price * cart_info[key]
        sum_in_cart += sum_product
    try:
        discount_code = request.session.get('discount')
        discount = Discount.objects.get(code__exact=discount_code)
        if discount:
            sum_in_cart = round(sum_in_cart * Decimal(1 - discount.value / 100))
    except Discount.DoesNotExist:
        pass

    return {
        'categories': categories,
        'search_form': search_form,
        'count_in_cart': count_in_cart,
        'sum_in_cart': sum_in_cart
    }
