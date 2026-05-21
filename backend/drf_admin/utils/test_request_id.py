# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from drf_admin.utils.request_id import (
    REQUEST_ID_HEADER,
    RequestIdMiddleware,
    get_request_id,
)


class RequestIdMiddlewareTests(TestCase):
    """验证 Django 请求链路中的 request id 生命周期。"""

    def setUp(self):
        self.factory = RequestFactory()

    def test_request_id_header_is_reused_and_cleared(self):
        request_id = "trace-from-client"
        request = self.factory.get("/health", HTTP_X_REQUEST_ID=request_id)

        def get_response(inner_request):
            self.assertEqual(inner_request.request_id, request_id)
            self.assertEqual(get_request_id(), request_id)
            return HttpResponse("ok")

        response = RequestIdMiddleware(get_response)(request)

        self.assertEqual(response[REQUEST_ID_HEADER], request_id)
        self.assertIsNone(get_request_id())

    def test_request_id_is_generated_when_missing(self):
        request = self.factory.get("/health")

        response = RequestIdMiddleware(lambda _request: HttpResponse("ok"))(request)

        self.assertTrue(response[REQUEST_ID_HEADER])
        self.assertEqual(response[REQUEST_ID_HEADER], request.request_id)
        self.assertIsNone(get_request_id())
