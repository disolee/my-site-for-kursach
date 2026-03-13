from .cart import Cart

def cart(request):
    """Добавляет корзину в контекст всех шаблонов"""
    return {'cart': Cart(request)}