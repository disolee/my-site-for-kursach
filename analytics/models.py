import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Event(models.Model):
    """Модель для хранения всех событий"""
    
    EVENT_TYPES = [
        ('view', 'Просмотр'),
        ('cart', 'Добавление в корзину'),
        ('purchase', 'Покупка'),
        ('search', 'Поиск'),
        ('wishlist', 'Избранное'),
        ('review', 'Отзыв'),
        ('logout', 'Выход'),
        ('registration', 'Регистрация'),
    ]
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    session_key = models.CharField(max_length=40, db_index=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    
    # Данные о продукте (связь с вашим приложением main)
    product = models.ForeignKey(
        'main.Product', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    product_name = models.CharField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    # Поисковые запросы
    search_query = models.CharField(max_length=500, null=True, blank=True)
    
    # Технические данные
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    referer = models.URLField(max_length=500, blank=True)
    path = models.CharField(max_length=500, blank=True)
    
    # Временные метки
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_key', 'created_at']),
            models.Index(fields=['category', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.user or self.session_key}"


class ReportSubscription(models.Model):
    """Подписки на регулярные отчеты"""
    
    SCHEDULES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
    ]
    
    REPORT_TYPES = [
        ('top_products', 'Топ товаров'),
        ('conversion', 'Конверсия'),
        ('sales', 'Продажи'),
        ('user_activity', 'Активность пользователей'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report_subscriptions'
    )
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    schedule = models.CharField(max_length=20, choices=SCHEDULES)
    parameters = models.JSONField(default=dict)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'report_type', 'schedule']
    
    def __str__(self):
        return f"{self.user.email} - {self.report_type}"


class ProductAnalytics(models.Model):
    """Кэшированная аналитика по товарам"""
    
    product = models.OneToOneField(
        'main.Product',  # Ваша модель Product из приложения main
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    views_count = models.PositiveIntegerField(default=0)
    cart_adds_count = models.PositiveIntegerField(default=0)
    purchases_count = models.PositiveIntegerField(default=0)
    wishlist_adds_count = models.PositiveIntegerField(default=0)
    
    view_to_cart_rate = models.FloatField(default=0.0)
    cart_to_purchase_rate = models.FloatField(default=0.0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    last_purchased_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Analytics: {self.product.name}"


class HourlyStats(models.Model):
    """Почасовые агрегаты"""
    
    hour = models.DateTimeField(db_index=True)
    event_type = models.CharField(max_length=20, db_index=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    events_count = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    unique_sessions = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['hour', 'event_type', 'category']
        ordering = ['-hour']


class DailyStats(models.Model):
    """Ежедневные агрегаты"""
    
    date = models.DateField(db_index=True)
    event_type = models.CharField(max_length=20, db_index=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    events_count = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    unique_sessions = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['date', 'event_type', 'category']
        ordering = ['-date']