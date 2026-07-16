from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm, CartUpdateForm
from analytics.signals import EventTracker


def home(request):
    """Главная страница"""
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {'categories': categories})


def rings_catalog(request):
    """Каталог колец"""
    products = Product.objects.filter(category__slug='rings', available=True)
    return render(request, 'shop/rings.html', {  
        'products': products,
        'category_name': 'RINGS'
    })


def tees_catalog(request):
    """Каталог футболок"""
    products = Product.objects.filter(category__slug='tees', available=True)
    return render(request, 'shop/tees.html', {  
        'products': products,
        'category_name': 'TEES'
    })


def hoodies_catalog(request):
    """Каталог худи"""
    products = Product.objects.filter(category__slug='hoodies', available=True)
    return render(request, 'shop/hoodies.html', { 
        'products': products,
        'category_name': 'HOODIES'
    })


def pendants_catalog(request):
    """Каталог подвесок"""
    products = Product.objects.filter(category__slug='pendants', available=True)
    return render(request, 'shop/pendants.html', { 
        'products': products,
        'category_name': 'PENDANTS'
    })


def outerwear_catalog(request):
    """Каталог верхней одежды"""
    products = Product.objects.filter(category__slug='outerwear', available=True)
    return render(request, 'shop/outerwear.html', {  
        'products': products,
        'category_name': 'OUTERWEAR'
    })


def cart_detail(request):
    """Страница корзины"""
    cart = Cart(request)
    
    if request.method == 'POST':
        for item in cart:
            update_key = f'update_{item["product"].id}'
            if update_key in request.POST:
                try:
                    quantity = int(request.POST.get('quantity', 1))
                    if quantity > 0:
                        cart.update(item['product'], quantity)
                        messages.success(request, 'Количество обновлено')
                    else:
                        cart.remove(item['product'])
                        messages.info(request, 'Товар удалён из корзины')
                except (ValueError, TypeError):
                    messages.error(request, 'Неверное количество')
                return redirect('cart_detail')
    
    return render(request, 'shop/cart.html', {'cart': cart})

def cart_add(request, product_id):
    """Добавить товар в корзину"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        cart.add(product=product, quantity=quantity, update_quantity=cd.get('update', False))
        EventTracker.track(request, 'cart', product=product, quantity=quantity)
        messages.success(request, f'{product.name} добавлен в корзину')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def cart_remove(request, product_id):
    """Удалить товар из корзины"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'{product.name} удалён из корзины')
    return redirect('cart_detail')


def cart_clear(request):
    """Очистить корзину"""
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Корзина очищена')
    return redirect('cart_detail')

from django.db import transaction
from .models import Product, Category, Order, OrderItem
from .forms import CartAddProductForm, CartUpdateForm, CheckoutForm

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Корзина пуста')
        return redirect('cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    total_amount=cart.get_total_price(),
                    **cd
                )
                for item in cart:
                    if item['quantity'] > item['product'].quantity:
                        messages.error(request, f"Недостаточно {item['product'].name} на складе")
                        return redirect('cart_detail')
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['price'],
                    )
                    item['product'].decrease_quantity(item['quantity'])
                    EventTracker.track(request, 'purchase', product=item['product'], quantity=item['quantity'])
                cart.clear()
            return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {'cart': cart, 'form': form})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    EventTracker.track(request, 'view', product=product)
    
    recommended = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'recommended': recommended
    })

def ai_assistant(request):
    return render(request, 'shop/ai_assistant.html')

def about(request):
    """Страница 'О нас'"""
    return render(request, 'shop/about.html')