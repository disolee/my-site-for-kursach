from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Initialize analytics database indexes'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating indexes for analytics...')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS 
                    analytics_event_created_at_idx ON analytics_event (created_at DESC)
                """)
                self.stdout.write('✓ Created index: analytics_event_created_at_idx')
            except Exception as e:
                self.stdout.write(f'✗ Error: {e}')
            
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS 
                    analytics_event_type_created_idx ON analytics_event (event_type, created_at DESC)
                """)
                self.stdout.write('✓ Created index: analytics_event_type_created_idx')
            except Exception as e:
                self.stdout.write(f'✗ Error: {e}')
            
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS 
                    analytics_event_user_created_idx ON analytics_event (user_id, created_at DESC)
                """)
                self.stdout.write('✓ Created index: analytics_event_user_created_idx')
            except Exception as e:
                self.stdout.write(f'✗ Error: {e}')
        
        self.stdout.write(self.style.SUCCESS('Analytics initialization completed!'))