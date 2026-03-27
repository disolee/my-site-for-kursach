from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Event, ProductAnalytics


class ReportGenerator:
    
    @staticmethod
    def get_conversion_report(days=7):
        since = timezone.now() - timedelta(days=days)
        
        stats = Event.objects.filter(created_at__gte=since).aggregate(
            views=Count('id', filter=Q(event_type='view')),
            carts=Count('id', filter=Q(event_type='cart')),
            purchases=Count('id', filter=Q(event_type='purchase')),
            unique_users=Count('user_id', distinct=True),
            unique_sessions=Count('session_key', distinct=True),
        )
        
        stats['view_to_cart_rate'] = (stats['carts'] / stats['views'] * 100) if stats['views'] > 0 else 0
        stats['cart_to_purchase_rate'] = (stats['purchases'] / stats['carts'] * 100) if stats['carts'] > 0 else 0
        stats['overall_conversion'] = (stats['purchases'] / stats['views'] * 100) if stats['views'] > 0 else 0
        
        # Ежедневная динамика
        daily = Event.objects.filter(created_at__gte=since).extra(
            {'date': "DATE(created_at)"}
        ).values('date', 'event_type').annotate(count=Count('id'))
        
        daily_stats = {}
        for item in daily:
            d = item['date'].isoformat()
            if d not in daily_stats:
                daily_stats[d] = {'views': 0, 'carts': 0, 'purchases': 0}
            daily_stats[d][item['event_type']] = item['count']
        
        stats['daily_data'] = [{'date': k, **v} for k, v in daily_stats.items()]
        return stats
    
    @staticmethod
    def get_top_products_report(days=7, limit=10, category=None):
        since = timezone.now() - timedelta(days=days)
        qs = Event.objects.filter(created_at__gte=since, event_type='view')
        
        if category:
            qs = qs.filter(category=category)
        
        products = qs.values('product_id', 'product_name').annotate(
            views=Count('id'),
            unique_users=Count('user_id', distinct=True)
        ).order_by('-views')[:limit]
        
        result = []
        for p in products:
            item = {
                'product_id': p['product_id'],
                'product_name': p['product_name'] or str(p['product_id'])[:8],
                'views': p['views'],
                'unique_users': p['unique_users'],
            }
            if p['product_id']:
                try:
                    a = ProductAnalytics.objects.get(product_id=p['product_id'])
                    item['view_to_cart_rate'] = a.view_to_cart_rate
                    item['purchases'] = a.purchases_count
                except ProductAnalytics.DoesNotExist:
                    item['view_to_cart_rate'] = 0
                    item['purchases'] = 0
            result.append(item)
        
        return result
    
    @staticmethod
    def get_sales_report(days=7):
        since = timezone.now() - timedelta(days=days)
        
        sales = Event.objects.filter(created_at__gte=since, event_type='purchase').aggregate(
            total_orders=Count('id', distinct=True),
            total_items=Sum('quantity'),
            total_revenue=Sum('price'),
            avg_order_value=Avg('price'),
            unique_customers=Count('user_id', distinct=True),
        )
        
        daily = Event.objects.filter(created_at__gte=since, event_type='purchase').extra(
            {'date': "DATE(created_at)"}
        ).values('date').annotate(
            orders=Count('id'),
            revenue=Sum('price'),
            items=Sum('quantity')
        ).order_by('date')
        
        return {**sales, 'daily_sales': list(daily)}
    
    @staticmethod
    def get_user_activity_report(days=7):
        since = timezone.now() - timedelta(days=days)
        
        activity = Event.objects.filter(created_at__gte=since).aggregate(
            active_users=Count('user_id', distinct=True),
            active_sessions=Count('session_key', distinct=True),
            total_events=Count('id'),
        )
        activity['avg_events_per_user'] = activity['total_events'] / max(activity['active_users'], 1)
        
        hourly = Event.objects.filter(created_at__gte=since).extra(
            {'hour': "EXTRACT(hour FROM created_at)"}
        ).values('hour').annotate(events=Count('id')).order_by('hour')
        
        return {**activity, 'hourly_activity': list(hourly)}
    
    @staticmethod
    def generate_report(report_type, params):
        days = params.get('days', 7)
        limit = params.get('limit', 10)
        
        if report_type == 'conversion':
            data = ReportGenerator.get_conversion_report(days)
            text = f"""
==========================================
ОТЧЕТ ПО КОНВЕРСИИ за {days} дней
==========================================

📊 ОСНОВНЫЕ ПОКАЗАТЕЛИ:
• Просмотры: {data['views']:,}
• Корзины: {data['carts']:,}
• Покупки: {data['purchases']:,}
• Уникальные пользователи: {data['unique_users']:,}
• Уникальные сессии: {data['unique_sessions']:,}

📈 КОНВЕРСИЯ:
• Просмотр → Корзина: {data['view_to_cart_rate']:.1f}%
• Корзина → Покупка: {data['cart_to_purchase_rate']:.1f}%
• Общая конверсия: {data['overall_conversion']:.1f}%

==========================================
"""
            html = f"""
<!DOCTYPE html>
<html>
<head><style>
body {{ font-family: Arial, sans-serif; }}
.header {{ background: #007bff; color: white; padding: 20px; }}
.metric {{ margin: 20px 0; padding: 15px; background: #f8f9fa; }}
.value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
</style></head>
<body>
<div class="header"><h1>Отчет по конверсии за {days} дней</h1></div>
<div class="metric">
<h3>Основные показатели</h3>
<p>Просмотры: <span class="value">{data['views']:,}</span></p>
<p>Корзины: <span class="value">{data['carts']:,}</span></p>
<p>Покупки: <span class="value">{data['purchases']:,}</span></p>
</div>
<div class="metric">
<h3>Конверсия</h3>
<p>Просмотр → Корзина: <b>{data['view_to_cart_rate']:.1f}%</b></p>
<p>Корзина → Покупка: <b>{data['cart_to_purchase_rate']:.1f}%</b></p>
</div>
</body>
</html>
"""
        
        elif report_type == 'top_products':
            data = ReportGenerator.get_top_products_report(days, limit)
            text = f"ТОП-{limit} ТОВАРОВ за {days} дней:\n\n"
            for i, p in enumerate(data, 1):
                text += f"{i}. {p['product_name']}\n"
                text += f"   Просмотров: {p['views']:,}\n"
                text += f"   Уникальных пользователей: {p['unique_users']}\n\n"
            
            html = f"<h2>Топ {limit} товаров за {days} дней</h2><ul>"
            for p in data:
                html += f"<li><b>{p['product_name']}</b> - {p['views']} просмотров</li>"
            html += "</ul>"
        
        else:
            data = ReportGenerator.get_sales_report(days)
            text = f"""
ОТЧЕТ ПО ПРОДАЖАМ за {days} дней:
--------------------------------
• Заказов: {data['total_orders']:,}
• Продано товаров: {data['total_items']:,}
• Выручка: {data['total_revenue']:,.2f} ₽
• Средний чек: {data['avg_order_value']:,.2f} ₽
• Уникальных покупателей: {data['unique_customers']:,}
"""
            html = f"<h2>Продажи за {days} дней</h2><p>Выручка: {data['total_revenue']:,.2f} ₽<br>Заказов: {data['total_orders']}</p>"
        
        return {'text': text, 'html': html, 'data': data}