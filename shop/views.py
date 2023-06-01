from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic

from shop.forms import SearchForm
from shop.models import Category, Product


def index(request):
    products = Product.objects.all().order_by(get_order_by_products(request))[:8]
    context = {'products': products}
    # return HttpResponse('Test')
    return render(
        request,
        'index.html',
        context=context
    )


def get_order_by_products(request):
    order_by = '-date'
    if request.GET.__contains__('sort') and request.GET.__contains__('up'):
        sort = request.GET['sort']
        up = request.GET['up']
        if sort == 'price' or sort == 'name':
            order_by = '-' if up == '0' else ''
            order_by += sort
        print(order_by)
    return order_by


def delivery(request):
    return render(
        request,
        'delivery.html'
    )


def contacts(request):
    return render(
        request,
        'contacts.html'
    )


def category(request, id):
    obj = get_object_or_404(Category, pk=id)
    print(obj.id)
    products = Product.objects.filter(category__exact=obj).order_by(get_order_by_products(request))[:8]
    print(products)
    context = {'category': obj, 'products': products}
    return render(
        request,
        'category.html',
        context=context
    )


def about(request):
    return render(
        request,
        'about.html'
    )


class ProductDetailView(generic.DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.\
            filter(category__exact=self.get_object().category).\
            exclude(id=self.get_object().id).order_by('?')[:4]
        return context


def handler404(request):
    return render(request, '404.html', status=404)


def search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        q = search_form.cleaned_data['q']
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
        context = {'products': products, 'q': q}
        return render(
            request,
            'search.html',
            context
        )
