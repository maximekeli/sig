"""Ajoute uniquement les fiches géomatique et SIG."""
from django.core.management.base import BaseCommand

from education.models import PedagogicalSheet
from education.sheets_data import GEOMATIC_SIG_SHEETS


class Command(BaseCommand):
    help = 'Crée ou met à jour les fiches sur la géomatique et les SIG.'

    def handle(self, *args, **options):
        for title, theme, order, content in GEOMATIC_SIG_SHEETS:
            PedagogicalSheet.objects.update_or_create(
                title=title,
                defaults={'theme': theme, 'content_fr': content, 'order': order},
            )
            self.stdout.write(f'  ✓ {title}')
        self.stdout.write(
            self.style.SUCCESS(
                f'Géomatique / SIG : {len(GEOMATIC_SIG_SHEETS)} fiche(s). '
                f'Total : {PedagogicalSheet.objects.count()}',
            ),
        )
