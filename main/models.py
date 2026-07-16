from django.db import models
from django.urls import reverse

class Category(models.Model):
    """Категория товара (Кольца, Майки, и т.д.)"""
    name = models.CharField(
        max_length=100, 
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True, 
        verbose_name='URL-слаг',
        help_text='Например: rings, tees, hoodies'
    )
    description = models.TextField(
        blank=True, 
        verbose_name='Описание категории'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Товар магазина"""
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name='Категория'
    )
    name = models.CharField(
        max_length=200, 
        verbose_name='Название товара'
    )
    slug = models.SlugField(
        unique=True, 
        verbose_name='URL-слаг',
        help_text='Например: lunar-signet-ring'
    )
    description = models.TextField(
        verbose_name='Описание товара',
        help_text='Полное описание для страницы товара'
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Краткое описание',
        help_text='Для превью в каталоге'
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Цена'
    )
    quantity = models.PositiveIntegerField(
        default=0, 
        verbose_name='Количество на складе',
        help_text='Сколько штук доступно для покупки'
    )
    symbol = models.CharField(
        max_length=10, 
        blank=True, 
        default='◈',
        verbose_name='Символ/Иконка',
        help_text='Эмодзи или символ для отображения (☾, ✖, ▲, †, ⛓)'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d', 
        blank=True, 
        null=True,
        verbose_name='Изображение товара'
    )
    available = models.BooleanField(
        default=True, 
        verbose_name='Доступен для покупки'
    )
    created = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата добавления'
    )
    updated = models.DateTimeField(
        auto_now=True, 
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']  
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['category', 'available']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    def is_in_stock(self):
        """Проверка наличия"""
        return self.quantity > 0 and self.available
    
    def decrease_quantity(self, amount=1):
        """Уменьшить количество на складе"""
        if self.quantity >= amount:
            self.quantity -= amount
            self.save()
            return True
        return False
    
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user or self.email}"


class OrderItem(models.Model):
    """Модель товара в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"