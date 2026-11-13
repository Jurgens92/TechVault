"""Pagination classes for TechVault."""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Page-number pagination that lets clients request a larger page (capped)."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000
