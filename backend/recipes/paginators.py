from rest_framework.paginasubscribe_totion import \
    PageNumbesubscribe_torPagination


class PageNumberPaginatorModified(PageNumberPagination):
    page_size_query_param = 'limit'
