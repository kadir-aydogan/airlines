from rest_framework import serializers

from apps.core.models import Flight, Airplane

from apps.core.services.flight_services import FlightCreateInput, FlightUpdateInput
from django.utils import timezone

class FlightListSerializer(serializers.ModelSerializer):

    airplane_id = serializers.IntegerField(source="airplane.id", read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "airplane_id",
            "departure", "destination",
            "departure_time", "arrival_time",
        )

class FlightCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    flight_number   = serializers.CharField(max_length=20)
    departure       = serializers.CharField(max_length=20)
    destination     = serializers.CharField(max_length=20)
    departure_time  = serializers.DateTimeField()
    arrival_time    = serializers.DateTimeField()
    airplane        = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.only("id"))

    def validate(self, attrs):
        dep = attrs["departure_time"]
        arr = attrs["arrival_time"]

        if arr <= dep:
            raise serializers.ValidationError({"arrival_time": "Arrival must be after departure."})

        # USE_TZ=True ise aware tarih beklemek en doğrusu
        if timezone.is_naive(dep) or timezone.is_naive(arr):
            raise serializers.ValidationError("Datetime values must be timezone-aware (ISO8601 with offset).")

        if attrs["departure"].strip().upper() == attrs["destination"].strip().upper():
            raise serializers.ValidationError({"destination": "Destination must differ from departure."})

        return attrs

    def to_input(self) -> FlightCreateInput:
        v = self.validated_data
        return FlightCreateInput(
            flight_number=v["flight_number"],
            departure=v["departure"],
            destination=v["destination"],
            departure_time=v["departure_time"],
            arrival_time=v["arrival_time"],
            airplane_id=v["airplane"].id,
        )

class FlightsQuerySerializer(serializers.Serializer):
    airplane_id = serializers.IntegerField(required=False, min_value=1)
    departure = serializers.CharField(required=False)
    destination = serializers.CharField(required=False)
    departure_time = serializers.DateTimeField(required=False)
    arrival_time = serializers.DateTimeField(required=False)
    search = serializers.CharField(required=False)

    ordering = serializers.ChoiceField(
        required=False,
        choices=["departure_time", "-departure_time", "arrival_time", "-arrival_time"]
    )

class FlightUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    flight_number = serializers.CharField(max_length=20)
    departure = serializers.CharField(max_length=20)
    destination = serializers.CharField(max_length=20)
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.only("id"))

    def validate(self, attrs):
        dep = attrs["departure_time"]
        arr = attrs["arrival_time"]

        if arr <= dep:
            raise serializers.ValidationError({"arrival_time": "Arrival must be after departure."})

        # USE_TZ=True ise aware tarih beklemek en doğrusu
        if timezone.is_naive(dep) or timezone.is_naive(arr):
            raise serializers.ValidationError("Datetime values must be timezone-aware (ISO8601 with offset).")

        if attrs["departure"].strip().upper() == attrs["destination"].strip().upper():
            raise serializers.ValidationError({"destination": "Destination must differ from departure."})
        return attrs

    def to_input(self) -> FlightUpdateInput:
        v = self.validated_data
        return FlightUpdateInput(
            flight_number=v["flight_number"],
            departure=v["departure"],
            destination=v["destination"],
            departure_time=v["departure_time"],
            arrival_time=v["arrival_time"],
            airplane_id=v["airplane"].id,
        )