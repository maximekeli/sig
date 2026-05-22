"""Ajoute les fiches pédagogiques supplémentaires (sols + géomatique/SIG)."""
from django.core.management.base import BaseCommand

from education.models import PedagogicalSheet
from education.sheets_data import EXTRA_PEDAGOGICAL_SHEETS, GEOMATIC_SIG_SHEETS


class Command(BaseCommand):
    help = 'Crée ou met à jour les fiches pédagogiques supplémentaires (sols, géomatique, SIG).'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        all_sheets = list(EXTRA_PEDAGOGICAL_SHEETS) + list(GEOMATIC_SIG_SHEETS)
        for title, theme, order, content in all_sheets:
            obj, was_created = PedagogicalSheet.objects.update_or_create(
                title=title,
                defaults={'theme': theme, 'content_fr': content, 'order': order},
            )
            if was_created:
                created += 1
            else:
                updated += 1
            self.stdout.write(f'  {"+" if was_created else "~"} {title} (ordre {order})')
        self.stdout.write(
            self.style.SUCCESS(
                f'Fiches supplémentaires : {created} créée(s), {updated} mise(s) à jour. '
                f'Total en base : {PedagogicalSheet.objects.count()}',
            ),
        )
