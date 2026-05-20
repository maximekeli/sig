"""Utilitaires admin Django pour tables à 10M+ lignes (PostGIS/PostgreSQL)."""
from django.core.paginator import Paginator
from django.db import connection
from django.utils.functional import cached_property


def pg_table_row_estimate(model) -> int | None:
    """Estimation rapide via pg_class.reltuples (pas de COUNT(*))."""
    if connection.vendor != 'postgresql':
        return None
    table = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COALESCE(c.reltuples::bigint, 0)
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = %s AND n.nspname = ANY (current_schemas(FALSE))
            """,
            [table],
        )
        row = cursor.fetchone()
    return int(row[0]) if row else None


class LargeTablePaginator(Paginator):
    """
    Évite COUNT(*) sur toute la table quand la liste admin n'est pas filtrée.
    Avec des filtres actifs, exécute un COUNT borné par la clause WHERE.
    """

    @cached_property
    def count(self):
        qs = self.object_list
        if qs.query.where:
            return qs.order_by().count()
        estimate = pg_table_row_estimate(qs.model)
        if estimate is not None and estimate > 0:
            return estimate
        return 10_000_000


class LargeTableAdminMixin:
    """À mixer dans ModelAdmin pour listes volumineuses."""

    show_full_result_count = False
    paginator = LargeTablePaginator
    list_per_page = 50
