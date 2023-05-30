from shop.models import Category


def add_default_data(request):
    categories = Category.objects.all()
    return {'categories': categories}
