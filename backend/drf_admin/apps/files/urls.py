from django.urls import path

from drf_admin.apps.files.views import FileAPIView

urlpatterns = [
    path('', FileAPIView.as_view()),
]
