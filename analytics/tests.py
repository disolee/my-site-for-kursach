from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Event
from .reports import ReportGenerator

class ConversionReportTests(TestCase):
    def test_only_counts_events_within_window(self):
        old = timezone.now() - timedelta(days=30)
        recent = timezone.now()
        Event.objects.create(event_type='view', session_key='s1', created_at=old)
        Event.objects.create(event_type='view', session_key='s2', created_at=recent)

        report = ReportGenerator.get_conversion_report(days=7)
        self.assertEqual(report['views'], 1)  # только событие за последние 7 дней