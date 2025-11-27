from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Базовый пагинатор для API:
    - page_size по умолчанию 50
    - поддержка параметра ?page_size=
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1000



