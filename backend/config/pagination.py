"""Pagination efficace pour grandes tables (10M+ lignes)."""
from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class LargeTableCursorPagination(CursorPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-id'
