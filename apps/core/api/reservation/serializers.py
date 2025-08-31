from rest_framework import serializers

from apps.core.api.flight.serializers import FlightListSerializer
from apps.core.models import Reservation, Flight
from apps.core.services.reservation_services import make_reservation, MakeReservationInput, UpdateReservationInput


class ReservationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = (
            "id",
            "reservation_code",
            "flight",
            "passenger_email",
            "passenger_name",
            "status",
            "created_at",
        )

class ReservationCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    passenger_name  = serializers.CharField(max_length=40)
    passenger_email = serializers.EmailField(max_length=254)
    flight          = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.only("id"))
    status          = serializers.BooleanField(required=False, default=True)

    def validate_passenger_name(self, v):
        v = v.strip()
        if not v:
            raise serializers.ValidationError("Name cannot be blank.")
        return v

    def validate_passenger_email(self, v):
        return v.strip().lower()

    def to_input(self) -> MakeReservationInput:
        v = self.validated_data
        return MakeReservationInput(
            passenger_name=v["passenger_name"],
            passenger_email=v["passenger_email"],
            flight_id=v["flight"].id,
            status=v.get("status", True),
        )

class ReservationUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    passenger_name  = serializers.CharField(max_length=40)
    passenger_email = serializers.EmailField(max_length=254)
    flight          = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.only("id"))
    status          = serializers.BooleanField(required=False, default=True)

    def validate_passenger_name(self, v):
        v = v.strip()
        if not v:
            raise serializers.ValidationError("Name cannot be blank.")
        return v

    def validate_passenger_email(self, v):
        return v.strip().lower()

    def to_input(self) -> UpdateReservationInput:
        v = self.validated_data
        return UpdateReservationInput(
            passenger_name=v["passenger_name"],
            passenger_email=v["passenger_email"],
            flight_id=v["flight"].id,
            status=v.get("status", True),
        )


class ReservationsQuerySerializer(serializers.Serializer):
    status = serializers.BooleanField(required=False, default=True)
    passenger_email = serializers.CharField(required=False, allow_blank=True)
    passenger_name = serializers.CharField(required=False, allow_blank=True)
    flight_id = serializers.IntegerField(required=False)
    ordering = serializers.ChoiceField(
        required = False,
        choices = ["id", "-id"]
    )

class ReservationDetailSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "reservation_code",
            "passenger_name",
            "passenger_email",
            "status",
            "flight",
        )
