import re
import logging
from django.utils.deprecation import MiddlewareMixin
from .signals import EventTracker

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(MiddlewareMixin):
    """Автоматический трекинг просмотров страниц"""

    IGNORE_PATHS = [
        r'^/admin/',
        r'^/static/',
        r'^/media/',
        r'^/favicon\.ico$',
        r'^/analytics/',
    ]

    def process_response(self, request, response):
        if not hasattr(request, 'session'):
            return response

        path = request.path
        for pattern in self.IGNORE_PATHS:
            if re.match(pattern, path):
                return response

        if request.method == 'GET' and response.status_code == 200:
            if not getattr(request, '_analytics_tracked', False):
                try:
                    EventTracker.track_page_view(request)
                    request._analytics_tracked = True
                except Exception:
                    logger.exception("Failed to track page view")

        return response