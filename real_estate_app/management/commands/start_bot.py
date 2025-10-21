from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Starts the Telegram bot'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        # Bot implementation will be added later