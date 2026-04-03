import re
import logging
from django.utils import timezone
from .tasks import process_event_async

logger = logging.getLogger(__name__)


class EventTracker:
    """Класс для трекинга событий"""
    
    @staticmethod
    def track(request, event_type, **kwargs):
        """Асинхронный трекинг события"""
        if not request:
            return
        
        if not request.session.session_key:
            request.session.save()
        
        # Передаем дату как строку в ISO формате
        now = timezone.now().isoformat()
        
        event_data = {
            'event_type': event_type,
            'session_key': request.session.session_key,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            'ip_address': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
            'referer': request.META.get('HTTP_REFERER', '')[:500],
            'path': request.path[:500],
            'created_at': now,
        }
        
        product = kwargs.get('product')
        if product:
            event_data.update({
                'product_id': product.id,
                'product_name': product.name,
                'category': product.category.name if hasattr(product, 'category') and product.category else None,
                'price': str(product.price),
                'quantity': kwargs.get('quantity', 1),
            })
        
        if kwargs.get('search_query'):
            event_data['search_query'] = kwargs['search_query'][:500]
        
        process_event_async.delay(event_data)
    
    @staticmethod
    def track_page_view(request):
        """Автоматический трекинг просмотра страницы"""
        if not request.session.session_key:
            request.session.save()
        
        now = timezone.now().isoformat()
        path = request.path
        
        # Проверяем URL товара
        match = re.search(r'/product/(\d+)/', path)
        if not match:
            match = re.search(r'/product/([^/]+)/', path)
        
        if match:
            try:
                from main.models import Product
                if not match.group(1).isdigit():
                    product = Product.objects.filter(slug=match.group(1)).first()
                else:
                    product = Product.objects.filter(id=match.group(1)).first()
                
                if product:
                    EventTracker.track(request, 'view', product=product)
                    return
            except Exception as e:
                logger.error(f"Error tracking product view: {e}")
        
        # Обычный просмотр страницы
        event_data = {
            'event_type': 'view',
            'session_key': request.session.session_key,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            'ip_address': request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
            'referer': request.META.get('HTTP_REFERER', '')[:500],
            'path': path[:500],
            'created_at': now,
        }
        
        process_event_async.delay(event_data)