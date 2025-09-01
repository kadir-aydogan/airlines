from django.utils import timezone
from rest_framework import serializers

from apps.core.models import Airplane
from apps.core.services.airplane_services import AirplaneCreateInput, AirplaneUpdateInput


class AirplaneCreateSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)

    tail_number     = serializers.CharField(max_length=20)
    model           = serializers.CharField(max_length=80)
    capacity        = serializers.IntegerField(min_value=1)
    production_year = serializers.IntegerField()
    status          = serializers.BooleanField(required=False, default=True)

    def validate_tail_number(self, v: str) -> str:
        v = v.strip()
        if not v:
            raise serializers.ValidationError("Tail number cannot be blank.")
        return v

    def validate_model(self, v: str) -> str:
        v = v.strip()
        if not v:
            raise serializers.ValidationError("Model cannot be blank.")
        return v

    def validate_production_year(self, value: int) -> int:
        now_year = timezone.now().year
        if value < 1950 or value > now_year:
            raise serializers.ValidationError(f"Must be between 1950 and {now_year}")
        return value

    def to_input(self) -> AirplaneCreateInput:
        v = self.validated_data
        return AirplaneCreateInput(
            tail_number=v["tail_number"],
            model=v["model"],
            capacity=v["capacity"],
            production_year=v["production_year"],
            status=v.get("status", True),
        )

class AirplaneUpdateSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)

    tail_number = serializers.CharField(required=False, max_length=20)
    model = serializers.CharField(required=False, max_length=80)
    capacity = serializers.IntegerField(required=False, min_value=1)
    production_year = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False, default=True)

    def validate_tail_number(self, v: str) -> str:
        v = v.strip()
        if not v:
            raise serializers.ValidationError("Tail number cannot be blank.")
        return v

    def validate_model(self, v: str) -> str:
        v = v.strip()
        if not v:
            raise serializers.ValidationError("Model cannot be blank.")
        return v

    def validate_production_year(self, value: int) -> int:
        now_year = timezone.now().year
        if value < 1950 or value > now_year:
            raise serializers.ValidationError(f"Must be between 1950 and {now_year}")
        return value

    def to_input(self) -> AirplaneUpdateInput:
        return AirplaneUpdateInput(**self.validated_data)

class AirplaneReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "tail_number", "model", "capacity", "production_year", "status")


class AirplaneQuerySerializer(serializers.Serializer):
    tail_number = serializers.CharField(required=False)
    model = serializers.CharField(required=False)
    min_capacity = serializers.IntegerField(required=False)
    max_capacity = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False, default=True)

    ordering = serializers.ChoiceField(
        required=False,
        choices=["id", "-id"]
    )

class AirplaneDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "tail_number",
            "model",
            "capacity",
            "production_year",
            "status",
        )

