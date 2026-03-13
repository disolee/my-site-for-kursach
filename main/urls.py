from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/rings/', views.rings_catalog, name='rings'),
    path('catalog/tees/', views.tees_catalog, name='tees'),
    path('catalog/hoodies/', views.hoodies_catalog, name='hoodies'),
    path('catalog/pendants/', views.pendants_catalog, name='pendants'),
    path('catalog/outerwear/', views.outerwear_catalog, name='outerwear'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('about/', views.about, name='about'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]