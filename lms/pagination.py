from rest_framework.pagination import PageNumberPagination

class PaginationOfTen(PageNumberPagination):
    page_size = 10
    page_query_parameter = 'page_size'
    max_size = 1000


class PaginationOfFifty(PageNumberPagination):
    page_size = 50
    page_query_param = 'page_size'
    max_size = 1000