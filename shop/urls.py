from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delivery', views.delivery, name='delivery'),
    path('contacts', views.contacts, name='contacts'),
    path('about', views.about, name='about'),
    re_path(r'category/(?P<id>\d+)$', views.category, name='category'),
    re_path(r'product/(?P<pk>\d+)$', views.ProductDetailView.as_view(), name='product'),
    path('search', views.search, name='search'),
    path('cart', views.cart, name='cart'),
    path('order', views.order, name='order'),
    path('addorder', views.addorder, name='addorder'),

]