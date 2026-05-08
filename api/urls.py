"""
URLs da API

    from django.urls import path, include
    urlpatterns = [
        ...
        path("api/", include("api.urls")),
    ]
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OcorrenciaViewSet

router = DefaultRouter()
router.register(r"ocorrencias", OcorrenciaViewSet, basename="ocorrencia")

urlpatterns = [
    path("", include(router.urls)),
]