import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q, Sum
from .models import Event, ProductAnalytics, HourlyStats, DailyStats, ReportSubscription

logger = logging.getLogger(__name__)


@shared_task
def process_event_async(event_data):
    """Асинхронная обработка события"""
    try:
        # Получаем created_at
        created_at = event_data.get('created_at')
        
        # Если это строка, конвертируем в datetime
        if created_at and isinstance(created_at, str):
            # Простой парсинг без использования dateutil
            import datetime
            # Убираем миллисекунды и временную зону
            created_at = created_at.replace('Z', '+00:00')
            if '.' in created_at:
                created_at = created_at.split('.')[0]
            # Парсим строку
            created_at = datetime.datetime.fromisoformat(created_at)
            # Добавляем часовой пояс
            created_at = timezone.make_aware(created_at)
        elif not created_at:
            created_at = timezone.now()
        
        with transaction.atomic():
            event = Event.objects.create(
                event_type=event_data.get('event_type'),
                session_key=event_data.get('session_key'),
                user_id=event_data.get('user_id'),
                user_agent=event_data.get('user_agent', '')[:500],
                ip_address=event_data.get('ip_address'),
                referer=event_data.get('referer', '')[:500],
                path=event_data.get('path', '')[:500],
                product_id=event_data.get('product_id'),
                product_name=event_data.get('product_name'),
                category=event_data.get('category'),
                price=event_data.get('price'),
                quantity=event_data.get('quantity', 1),
                search_query=event_data.get('search_query'),
                created_at=created_at,
            )
        
        # Обновляем аналитику товара
        if event_data.get('product_id'):
            analytics, _ = ProductAnalytics.objects.get_or_create(
                product_id=event_data['product_id']
            )
            
            if event_data['event_type'] == 'view':
                analytics.views_count += event_data.get('quantity', 1)
                analytics.last_viewed_at = timezone.now()
            elif event_data['event_type'] == 'cart':
                analytics.cart_adds_count += event_data.get('quantity', 1)
            elif event_data['event_type'] == 'purchase':
                quantity = event_data.get('quantity', 1)
                price = float(event_data.get('price', 0) or 0)
                analytics.purchases_count += quantity
                analytics.total_revenue += price * quantity
                analytics.last_purchased_at = timezone.now()
            
            analytics.save()
        
        # Обновляем агрегаты
        update_aggregates.delay()
        
        return f"Event {event.event_id} processed"
        
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise


@shared_task
def update_aggregates():
    """Обновление почасовых и ежедневных агрегатов"""
    now = timezone.now()
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    current_date = now.date()
    
    # Почасовые агрегаты
    stats = Event.objects.filter(
        created_at__gte=current_hour,
        created_at__lt=current_hour + timezone.timedelta(hours=1)
    ).values('event_type', 'category').annotate(
        events_count=Count('id'),
        unique_users=Count('user_id', distinct=True),
        unique_sessions=Count('session_key', distinct=True)
    )
    
    for stat in stats:
        HourlyStats.objects.update_or_create(
            hour=current_hour,
            event_type=stat['event_type'],
            category=stat['category'] or None,
            defaults={
                'events_count': stat['events_count'],
                'unique_users': stat['unique_users'],
                'unique_sessions': stat['unique_sessions'],
            }
        )
    
    # Ежедневные агрегаты
    daily_stats = Event.objects.filter(
        created_at__date=current_date
    ).values('event_type', 'category').annotate(
        events_count=Count('id'),
        unique_users=Count('user_id', distinct=True),
        unique_sessions=Count('session_key', distinct=True),
        total_revenue=Sum('price', filter=Q(event_type='purchase'))
    )
    
    for stat in daily_stats:
        DailyStats.objects.update_or_create(
            date=current_date,
            event_type=stat['event_type'],
            category=stat['category'] or None,
            defaults={
                'events_count': stat['events_count'],
                'unique_users': stat['unique_users'],
                'unique_sessions': stat['unique_sessions'],
                'total_revenue': stat['total_revenue'] or 0,
            }
        )
    
    return {"status": "completed"}


@shared_task
def cleanup_old_events():
    """Очистка старых событий"""
    from django.conf import settings
    days = settings.ANALYTICS.get('RETENTION_DAYS', 90)
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = Event.objects.filter(created_at__lt=cutoff).delete()
    return {"deleted": deleted}


@shared_task
def send_daily_reports():
    """Отправка ежедневных отчетов"""
    from django.core.mail import send_mail
    from django.conf import settings
    from .reports import ReportGenerator
    
    today = timezone.now().date()
    
    subscriptions = ReportSubscription.objects.filter(
        schedule='daily', 
        is_active=True
    ).exclude(last_sent__date=today)
    
    sent = 0
    for sub in subscriptions:
        try:
            report = ReportGenerator.generate_report(sub.report_type, sub.parameters)
            send_mail(
                subject=f"Отчет: {sub.get_report_type_display()}",
                message=report['text'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[sub.email],
                html_message=report['html']
            )
            sub.last_sent = timezone.now()
            sub.save()
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send report to {sub.email}: {e}")
    
    return {"sent": sent}