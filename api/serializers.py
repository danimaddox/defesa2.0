from rest_framework import serializers
from .models import Ocorrencia


class OcorrenciaSerializer(serializers.ModelSerializer):
    motivo_display = serializers.CharField(source="get_motivo_display", read_only=True)
    distrito_display = serializers.CharField(
        source="get_distrito_display", read_only=True
    )
    area_risco_display = serializers.CharField(
        source="get_area_risco_display", read_only=True
    )

    class Meta:
        model = Ocorrencia
        fields = [
            "id",
            "numero",
            "sigrc",
            "endereco",
            "bairro",
            "distrito",
            "distrito_display",
            "area_risco",
            "area_risco_display",
            "motivo",
            "motivo_display",
            "data",
            "latitude",
            "longitude",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def validate_area_risco(self, value):
        if value not in range(5):
            raise serializers.ValidationError("Nível de risco deve ser entre 0 e 4.")
        return value

    def validate(self, data):
        lat = data.get("latitude")
        lon = data.get("longitude")
        if (lat is None) != (lon is None):
            raise serializers.ValidationError(
                "Latitude e longitude devem ser fornecidas juntas."
            )
        return data


class OcorrenciaResumoSerializer(serializers.ModelSerializer):
    """Serializer compacto para listagens e análises."""

    class Meta:
        model = Ocorrencia
        fields = [
            "id",
            "numero",
            "bairro",
            "motivo",
            "area_risco",
            "data",
            "latitude",
            "longitude",
        ]


class EstatisticaSerializer(serializers.Serializer):
    """Serializer para os dados de análise/estatísticas."""

    total_ocorrencias = serializers.IntegerField()
    por_motivo = serializers.ListField(child=serializers.DictField())
    por_bairro = serializers.ListField(child=serializers.DictField())
    por_risco = serializers.ListField(child=serializers.DictField())
    por_mes = serializers.ListField(child=serializers.DictField())