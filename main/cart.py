from decimal import Decimal
from django.conf import settings
from main.models import Product


class Cart:
    def __init__(self, request):
        """Инициализация корзины"""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, update_quantity=False):
        """Добавить товар в корзину"""
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        if self.cart[product_id]['quantity'] > product.quantity:
            self.cart[product_id]['quantity'] = product.quantity
        
        self.save()
    
    def save(self):
        """Сохранить изменения в сессии"""
        self.session.modified = True
    
    def remove(self, product):
        """Удалить товар из корзины"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product, quantity):
        """Обновить количество товара"""
        product_id = str(product.id)
        if product_id in self.cart and quantity > 0:
            if quantity <= product.quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] = product.quantity
            self.save()
        elif quantity <= 0:
            self.remove(product)
    
    def __iter__(self):
        """Получить товары корзины — НЕ модифицирует self.cart!"""
        from decimal import Decimal
        
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {str(p.id): p for p in products}
        
        for product_id, item in self.cart.items():
            product = products_dict.get(product_id)
            if product:
                price = Decimal(item['price'])
                yield {
                    'product': product,
                    'quantity': item['quantity'],
                    'price': price,
                    'total_price': price * item['quantity']
                }
    
    def __len__(self):
        """Общее количество товаров"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """Общая стоимость"""
        from decimal import Decimal
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def clear(self):
        """Очистить корзину"""
        if 'cart' in self.session:
            del self.session['cart']
        self.save()