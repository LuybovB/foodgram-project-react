from rest_framework.pagination import PageNumberPagination

from foodgram.settings import P_SIZE


class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_size = P_SIZE
