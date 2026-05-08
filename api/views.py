from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from ocorrencias.models import Ocorrencia
from .serializers import (
    OcorrenciaSerializer,
    OcorrenciaResumoSerializer,
    EstatisticaSerializer,
)


#Filtro Personalizado

class OcorrenciaFilter(django_filters.FilterSet):
    """
    Filtros disponíveis:
      ?bairro=Jardim+Ângela
      ?motivo=Alagamento
      ?area_risco=3
      ?data_inicio=2025-01-01&data_fim=2025-12-31
      ?distrito=Jd.+Ângela
    """

    data_inicio = django_filters.DateFilter(field_name="data", lookup_expr="gte")
    data_fim = django_filters.DateFilter(field_name="data", lookup_expr="lte")
    bairro = django_filters.CharFilter(lookup_expr="icontains")
    motivo = django_filters.CharFilter(lookup_expr="iexact")
    distrito = django_filters.CharFilter(lookup_expr="iexact")
    area_risco = django_filters.NumberFilter()
    area_risco_min = django_filters.NumberFilter(
        field_name="area_risco", lookup_expr="gte"
    )

    class Meta:
        model = Ocorrencia
        fields = [
            "bairro",
            "motivo",
            "area_risco",
            "area_risco_min",
            "distrito",
            "data_inicio",
            "data_fim",
        ]


#ViewSet Principal

class OcorrenciaViewSet(viewsets.ModelViewSet):
    """
    API REST para Ocorrências da Defesa Civil.

    Endpoints:
      GET    /api/ocorrencias/           → lista todas (com filtros)
      POST   /api/ocorrencias/           → cria nova ocorrência
      GET    /api/ocorrencias/{id}/      → detalhe de uma ocorrência
      PUT    /api/ocorrencias/{id}/      → atualiza completamente
      PATCH  /api/ocorrencias/{id}/      → atualiza parcialmente
      DELETE /api/ocorrencias/{id}/      → remove

      GET    /api/ocorrencias/mapa/      → dados compactos para visualização no mapa
      GET    /api/ocorrencias/estatisticas/ → análise e totais agrupados
    """

    queryset = Ocorrencia.objects.all()
    serializer_class = OcorrenciaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OcorrenciaFilter
    search_fields = ["endereco", "bairro", "motivo", "numero"]
    ordering_fields = ["data", "area_risco", "bairro", "criado_em"]
    ordering = ["-data"]

    #Ação: dados para o mapa

    @action(detail=False, methods=["get"], url_path="mapa")
    def mapa(self, request):
        """
        Retorna apenas os campos necessários para plotar no mapa.
        Aceita os mesmos filtros do endpoint principal.
        Exemplo: GET /api/ocorrencias/mapa/?area_risco_min=3
        """
        qs = self.filter_queryset(self.get_queryset()).filter(
            latitude__isnull=False, longitude__isnull=False
        )
        serializer = OcorrenciaResumoSerializer(qs, many=True)
        return Response(
            {
                "count": qs.count(),
                "results": serializer.data,
            }
        )

    #Ação: estatísticas / análise de dados

    @action(detail=False, methods=["get"], url_path="estatisticas")
    def estatisticas(self, request):
        """
        Retorna análise agregada das ocorrências.
        Aceita filtros de data: ?data_inicio=2025-01-01&data_fim=2025-12-31

        Retorna:
          - total_ocorrencias
          - por_motivo       (motivo, total, ordenado decrescente)
          - por_bairro       (bairro, total, ordenado decrescente)
          - por_risco        (area_risco, total)
          - por_mes          (mes, total — últimos 12 meses)
        """
        qs = self.filter_queryset(self.get_queryset())

        total = qs.count()

        por_motivo = list(
            qs.values("motivo")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        por_bairro = list(
            qs.values("bairro")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        por_risco = list(
            qs.values("area_risco")
            .annotate(total=Count("id"))
            .order_by("area_risco")
        )

        por_mes = list(
            qs.annotate(mes=TruncMonth("data"))
            .values("mes")
            .annotate(total=Count("id"))
            .order_by("mes")
        )
        #Formata datas como string para serialização limpa
        for item in por_mes:
            item["mes"] = item["mes"].strftime("%Y-%m") if item["mes"] else None

        data = {
            "total_ocorrencias": total,
            "por_motivo": por_motivo,
            "por_bairro": por_bairro,
            "por_risco": por_risco,
            "por_mes": por_mes,
        }
        return Response(data, status=status.HTTP_200_OK)