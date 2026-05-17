from django.core.management.base import BaseCommand

from ml_predict.pipeline import train_and_save


class Command(BaseCommand):
    help = 'Train fertility classification model (OS5)'

    def add_arguments(self, parser):
        parser.add_argument('--algorithm', default='RandomForest')

    def handle(self, *args, **options):
        metrics = train_and_save(algorithm=options['algorithm'])
        self.stdout.write(self.style.SUCCESS(f'Model trained: F1={metrics["f1_macro"]:.3f}'))
