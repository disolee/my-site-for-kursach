from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import AnonymousUser
from .models import Category, Product

class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Tees', slug='tees')
        self.product = Product.objects.create(
            category=self.category, name='Test Tee', slug='test-tee',
            description='desc', price=Decimal('1000.00'), quantity=5
        )
        self.client = Client()

    def test_add_to_cart(self):
        response = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertIn(str(self.product.id), session['cart'])
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 2)

    def test_cart_respects_stock_limit(self):
        response = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 999})
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 5)

    def test_checkout_creates_order_and_decreases_stock(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        response = self.client.post('/checkout/', {
            'first_name': 'Тест', 'last_name': 'Тестов', 'email': 'test@test.com',
            'phone': '+79990000000', 'address': 'ул. Тестовая, 1', 'city': 'Москва',
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)
        self.assertEqual(response.status_code, 302)