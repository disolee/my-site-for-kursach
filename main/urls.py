from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rings/', views.rings_catalog, name='rings'),
    path('tees/', views.tees_catalog, name='tees'),
    path('hoodies/', views.hoodies_catalog, name='hoodies'),
    path('pendants/', views.pendants_catalog, name='pendants'),
    path('outerwear/', views.outerwear_catalog, name='outerwear'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('about/', views.about, name='about'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    path('ai/', include('ai_assistant.urls')),  
]