"""Ajoute les 5 fiches pédagogiques supplémentaires (sans réinitialiser la base)."""
from django.core.management.base import BaseCommand

from education.models import PedagogicalSheet
from education.sheets_data import EXTRA_PEDAGOGICAL_SHEETS


class Command(BaseCommand):
    help = 'Crée ou met à jour 5 fiches pédagogiques supplémentaires.'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for title, theme, order, content in EXTRA_PEDAGOGICAL_SHEETS:
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
