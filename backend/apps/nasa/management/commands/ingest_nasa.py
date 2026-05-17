from django.core.management.base import BaseCommand

from nasa.ingestion import enrich_soil_points_from_rasters, ingest_all


class Command(BaseCommand):
    help = 'Ingest NASA layers (earthaccess + STAC) and enrich soil points'

    def add_arguments(self, parser):
        parser.add_argument('--enrich-only', action='store_true')

    def handle(self, *args, **options):
        if options['enrich_only']:
            n = enrich_soil_points_from_rasters()
            self.stdout.write(self.style.SUCCESS(f'Enriched {n} soil points'))
            return
        result = ingest_all()
        self.stdout.write(self.style.SUCCESS(str(result)))
