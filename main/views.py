from django.shortcuts import render
from .models import Product, Category
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category
from .cart import Cart
from .forms import CartAddProductForm, CartUpdateForm


def home(request):
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {'categories': categories})


def rings_catalog(request):
    products = Product.objects.filter(category__slug='rings', available=True)
    return render(request, 'shop/rings.html', {  
        'products': products,
        'category_name': 'RINGS'
    })


def tees_catalog(request):
    products = Product.objects.filter(category__slug='tees', available=True)
    return render(request, 'shop/tees.html', {  
        'products': products,
        'category_name': 'TEES'
    })


def hoodies_catalog(request):
    products = Product.objects.filter(category__slug='hoodies', available=True)
    return render(request, 'shop/hoodies.html', { 
        'products': products,
        'category_name': 'HOODIES'
    })


def pendants_catalog(request):
    products = Product.objects.filter(category__slug='pendants', available=True)
    return render(request, 'shop/pendants.html', { 
        'products': products,
        'category_name': 'PENDANTS'
    })


def outerwear_catalog(request):
    products = Product.objects.filter(category__slug='outerwear', available=True)
    return render(request, 'shop/outerwear.html', {  
        'products': products,
        'category_name': 'OUTERWEAR'
    })

from django.shortcuts import redirect

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
        cart.add(product=product, quantity=cd['quantity'], update_quantity=cd.get('update', False))
        messages.success(request, f'{product.name} добавлен в корзину')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def cart_remove(request, product_id):
    """Удалить товар из корзины"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'{product.name} удалён из корзины')
    return redirect('cart_detail')

def product_detail(request, slug):
    """Страница отдельного товара"""
    product = get_object_or_404(Product, slug=slug, available=True)
    
    recommended = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'recommended': recommended
    })

def about(request):
    """Страница 'О нас'"""
    return render(request, 'shop/about.html')

def cart_clear(request):
    """Очистить корзину"""
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Корзина очищена')
    return redirect('cart_detail')