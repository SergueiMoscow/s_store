import datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic


from shop.forms import SearchForm, OrderModelForm, FeedbackForm
from shop.models import Category, Product, Discount, Order, OrderLine, Feedback


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
    if request.POST:
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = Feedback()
            feedback.client_name = form.cleaned_data['client_name']
            feedback.phone = form.cleaned_data['phone']
            feedback.email = form.cleaned_data['email']
            feedback.message = form.cleaned_data['message']
            feedback.status = 'New'
            feedback.save()
            print('saving feedback')
            return render(
                request,
                'feedback_sent.html'
            )
    else:
        form = FeedbackForm()
    context = {'form': form}
    return render(
        request,
        'contacts.html',
        context=context
    )


def category(request, id):
    print(f'Id: {id}')
    if id == 0:
        return index()
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


def order(request):
    cart_info = request.session.get('cart_info')
    if not cart_info:
        raise Http404()
    if request.method == 'POST':
        form = OrderModelForm(request.POST)
        if form.is_valid():
            order_obj = Order()
            order_obj.need_delivery = form.cleaned_data['delivery'] == 1
            discount_code = request.session.get('discount')
            if request.session.get('discount'):
                try:
                    discount = Discount.objects.get(code__exact=discount_code)
                    order_obj.discount = discount
                except Discount.DoesNotExist:
                    pass
            # now = datetime.datetime.now()
            # tz = timezone.get_current_timezone()
            # aware_datetime = timezone.make_aware(now, tz)

            order_obj.name = form.cleaned_data['name']
            order_obj.phone = form.cleaned_data['phone']
            order_obj.email = form.cleaned_data['email']
            order_obj.address = form.cleaned_data['address']
            order_obj.notice = form.cleaned_data['notice']
            # order_obj.date_order = '2023-06-07 10:00:00.23'
            # order_obj.date_send = '2023-06-07 10:01:00.24'
            order_obj.save()
            add_order_lines(request, order_obj)
            return HttpResponseRedirect(reverse('addorder'))
    else:
        form = OrderModelForm()
    context = {'form': form}
    return render(
        request,
        'order.html',
        context=context
    )


def add_order_lines(request, order_obj):
    cart_info = request.session.get('cart_info', {})
    for key in cart_info:
        order_line = OrderLine()
        order_line.order = order_obj
        order_line.product = get_object_or_404(Product, pk=key)
        order_line.price = order_line.product.price
        order_line.count = cart_info[key]
        order_line.save()
    # request.session.clear() # Стирает всю сессию, в том числе авторизацию
    del request.session['cart_info']


def addorder(request):
    return render(
        request,
        'addorder.html'
    )