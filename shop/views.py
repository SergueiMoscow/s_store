from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from shop.forms import SearchForm
from shop.models import Category, Product, Discount


def index(request):
    result = prerender(request)
    if result:
        return result
    products = Product.objects.all().order_by(get_order_by_products(request))[:8]
    context = {'products': products}
    # return HttpResponse('Test')
    return render(
        request,
        'index.html',
        context=context
    )


def prerender(request):
    if request.GET.get('add_cart'):
        product_id = request.GET.get('add_cart')
        get_object_or_404(Product, pk=product_id)
        cart_info = request.session.get('cart_info', {})
        count = cart_info.get(product_id, 0)
        count += 1
        cart_info.update({product_id: count})
        request.session['cart_info'] = cart_info
        print(cart_info)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


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
    result = prerender(request)
    if result:
        return result
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

    def get(self, request, *args, **kwargs):
        result = prerender(request)
        if result:
            return result
        return super(ProductDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.\
            filter(category__exact=self.get_object().category).\
            exclude(id=self.get_object().id).order_by('?')[:4]
        return context


def handler404(request):
    return render(request, '404.html', status=404)


def search(request):
    result = prerender(request)
    if result:
        return result
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        q = search_form.cleaned_data['q']
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 4)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        context = {'products': products, 'q': q}
        return render(
            request,
            'search.html',
            context
        )


def cart(request):
    result = update_cart_info(request)
    if result:
        return result
    cart_info = request.session.get('cart_info')
    products = []
    if cart_info:
        for product_id in cart_info:
            product = get_object_or_404(Product, pk=product_id)
            product.count = cart_info[product_id]
            products.append(product)
    context = {
        'products': products,
        'discount': request.session.get('discount', '')
    }
    return render(
        request,
        'cart.html',
        context=context
    )


def update_cart_info(request):
    if request.POST:
        cart_info = {}
        for param in request.POST:
            value = request.POST.get(param)
            if param.startswith('count_') and value.isnumeric():
                product_id = param.replace('count_', '')
                get_object_or_404(Product, pk=product_id)
                cart_info[product_id] = int(value)
            elif param == 'discount' and value:
                try:
                    discount = Discount.objects.get(code__exact=value)
                    request.session['discount'] = value
                    print("Discount passed")
                except Discount.DoesNotExist:
                    print(f"Discount {value} not passed")
                    pass

        request.session['cart_info'] = cart_info

    if request.GET:
        cart_info = request.session.get('cart_info')
        product_id = request.GET.get('delete_cart')
        get_object_or_404(Product, pk=product_id)
        current_count = cart_info.get(product_id, 0)
        if current_count <= 1:
            cart_info.pop(product_id)
        else:
            cart_info[product_id] -= 1
        request.session['cart_info'] = cart_info
        return HttpResponseRedirect(reverse('cart'))
