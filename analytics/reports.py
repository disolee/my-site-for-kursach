from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Event


class ReportGenerator:
    
    @staticmethod
    def get_conversion_report(days=7):
        """Отчет по конверсии - упрощенная версия"""
        since = timezone.now() - timedelta(days=days)
        
        # Простая статистика
        views = Event.objects.filter(event_type='view').count()
        carts = Event.objects.filter(event_type='cart').count()
        purchases = Event.objects.filter(event_type='purchase').count()
        unique_users = Event.objects.values('user_id').distinct().count()
        unique_sessions = Event.objects.values('session_key').distinct().count()
        
        # Конверсия
        view_to_cart = (carts / views * 100) if views > 0 else 0
        cart_to_purchase = (purchases / carts * 100) if carts > 0 else 0
        
        return {
            'views': views,
            'carts': carts,
            'purchases': purchases,
            'unique_users': unique_users,
            'unique_sessions': unique_sessions,
            'view_to_cart_rate': view_to_cart,
            'cart_to_purchase_rate': cart_to_purchase,
            'overall_conversion': (purchases / views * 100) if views > 0 else 0,
            'daily_data': []
        }
    
    @staticmethod
    def get_top_products_report(days=7, limit=10, category=None):
        """Топ товаров по просмотрам"""
        products = Event.objects.filter(event_type='view').values(
            'product_id', 'product_name'
        ).annotate(
            views=Count('id'),
            unique_users=Count('user_id', distinct=True)
        ).order_by('-views')[:limit]
        
        result = []
        for p in products:
            result.append({
                'product_id': p['product_id'],
                'product_name': p['product_name'] or f"Товар {p['product_id']}",
                'views': p['views'],
                'unique_users': p['unique_users'],
                'view_to_cart_rate': 0,
                'purchases': 0
            })
        
        return result
    
    @staticmethod
    def get_sales_report(days=7):
        """Отчет по продажам - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        # Получаем данные по покупкам
        purchase_events = Event.objects.filter(event_type='purchase')
        
        # Считаем количество
        total_orders = purchase_events.count()
        
        # Считаем сумму
        total_revenue_result = purchase_events.aggregate(total=Sum('price'))
        total_revenue = total_revenue_result['total'] or 0
        
        # Считаем количество товаров
        total_items_result = purchase_events.aggregate(total=Sum('quantity'))
        total_items = total_items_result['total'] or 0
        
        # Средний чек
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Уникальные покупатели
        unique_customers = purchase_events.values('user_id').distinct().count()
        
        return {
            'total_orders': total_orders,
            'total_items': total_items,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
            'unique_customers': unique_customers,
            'daily_sales': []
        }
    
    @staticmethod
    def get_user_activity_report(days=7):
        """Отчет по активности пользователей"""
        return {
            'active_users': Event.objects.values('user_id').distinct().count(),
            'active_sessions': Event.objects.values('session_key').distinct().count(),
            'total_events': Event.objects.count(),
            'avg_events_per_user': 0,
            'hourly_activity': []
        }
    
    @staticmethod
    def generate_report(report_type, params):
        """Генерация отчета в текстовом формате"""
        days = params.get('days', 7)
        
        if report_type == 'conversion':
            data = ReportGenerator.get_conversion_report(days)
            text = f"""
ОТЧЕТ ПО КОНВЕРСИИ за {days} дней
--------------------------------
Просмотры: {data['views']}
Корзины: {data['carts']}
Покупки: {data['purchases']}
Конверсия: {data['view_to_cart_rate']:.1f}% → {data['cart_to_purchase_rate']:.1f}%
"""
            html = f"<h2>Конверсия</h2><p>Просмотры: {data['views']}<br>Покупки: {data['purchases']}</p>"
        
        elif report_type == 'top_products':
            data = ReportGenerator.get_top_products_report(days, params.get('limit', 10))
            text = "ТОП ТОВАРОВ:\n"
            for i, p in enumerate(data, 1):
                text += f"{i}. {p['product_name']} - {p['views']} просмотров\n"
            html = "<h2>Топ товаров</h2><ul>" + "".join(f"<li>{p['product_name']} - {p['views']}</li>" for p in data) + "</ul>"
        
        else:
            data = ReportGenerator.get_sales_report(days)
            text = f"""
ПРОДАЖИ за {days} дней
--------------------
Заказов: {data['total_orders']}
Выручка: {data['total_revenue']:.2f} ₽
"""
            html = f"<h2>Продажи</h2><p>Выручка: {data['total_revenue']:.2f} ₽</p>"
        
        return {'text': text, 'html': html, 'data': data}