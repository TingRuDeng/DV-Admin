from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class GlobalPagination(PageNumberPagination):
    page_query_param = "page_num"
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "code": 20000,
                "msg": "成功",
                "errors": None,
                "data": {
                    "list": data,
                    "total": self.page.paginator.count,
                },
            }
        )
