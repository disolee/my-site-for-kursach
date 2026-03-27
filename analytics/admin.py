from django.contrib import admin
from .models import Event, ReportSubscription, ProductAnalytics, HourlyStats, DailyStats


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'session_key', 'product', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['user__email', 'session_key', 'product__name', 'product_name']
    readonly_fields = ['event_id']
    date_hierarchy = 'created_at'


@admin.register(ReportSubscription)
class ReportSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'schedule', 'is_active', 'last_sent']
    list_filter = ['report_type', 'schedule', 'is_active']
    search_fields = ['user__email', 'email']


@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'views_count', 'cart_adds_count', 'purchases_count', 'view_to_cart_rate']
    list_filter = ['product__category']
    search_fields = ['product__name']
    readonly_fields = ['view_to_cart_rate', 'cart_to_purchase_rate']


@admin.register(HourlyStats)
class HourlyStatsAdmin(admin.ModelAdmin):
    list_display = ['hour', 'event_type', 'events_count', 'unique_users']
    list_filter = ['event_type', 'hour']
    date_hierarchy = 'hour'


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'event_type', 'events_count', 'unique_users', 'total_revenue']
    list_filter = ['event_type', 'date']
    date_hierarchy = 'date'