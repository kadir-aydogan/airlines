from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.api.airplanes.serializers import AirplaneReadSerializer
from apps.core.models import Flight, Airplane
from apps.core.services.flight_services import FlightCreateInput, FlightUpdateInput


class FlightReadSerializer(serializers.ModelSerializer):

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
        if timezone.is_naive(dep):
            raise serializers.ValidationError({"departure_time": "Datetime values must be timezone-aware (ex: 2025-09-1T17:00:00+03:00)."})

        if timezone.is_naive(arr):
            raise serializers.ValidationError({"arrival_time": "Datetime values must be timezone-aware (ex: 2025-09-1T17:00:00+03:00)."})

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
    deleted = serializers.BooleanField(required=False, default=False)

    ordering = serializers.ChoiceField(
        required=False,
        choices=["departure_time", "-departure_time", "arrival_time", "-arrival_time"]
    )

class FlightUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    flight_number = serializers.CharField(required=False, max_length=20)
    departure = serializers.CharField(required=False, max_length=20)
    destination = serializers.CharField(required=False, max_length=20)
    departure_time = serializers.DateTimeField(required=False)
    arrival_time = serializers.DateTimeField(required=False)
    airplane = serializers.PrimaryKeyRelatedField(required=False, queryset=Airplane.objects.only("id"))

    def validate_departure_time(self, v):
        if timezone.is_naive(v):
            raise serializers.ValidationError({"departure_time": "Datetime values must be timezone-aware (ex: 2025-09-1T17:00:00+03:00)."})
        return v

    def validate_arrival_time(self, v):
        if timezone.is_naive(v):
            raise ValidationError({"arrival_time": "Datetime values must be timezone-aware (ex: 2025-09-1T17:00:00+03:00)."})
        return v

    def validate(self, attrs):
        dep_time = attrs.get("departure_time")
        arr_time = attrs.get("arrival_time")
        if dep_time is not None and arr_time is not None and arr_time <= dep_time:
            raise ValidationError({"arrival_time": "Arrival must be after departure."})

        dep = attrs.get("departure")
        dest = attrs.get("destination")
        if dep is not None and dest is not None and dep.strip().upper() == dest.strip().upper():
            raise ValidationError({"destination": "Destination must differ from departure."})
        return attrs

    def to_input(self) -> FlightUpdateInput:
        v = self.validated_data
        inst = self.instance

        pick = lambda name: v.get(name, getattr(inst, name))

        airplane_obj = v.get("airplane")
        airplane_id = airplane_obj.id if airplane_obj is not None else getattr(inst, "airplane_id", None)

        return FlightUpdateInput(
            flight_number=pick("flight_number"),
            departure=pick("departure"),
            destination=pick("destination"),
            departure_time=pick("departure_time"),
            arrival_time=pick("arrival_time"),
            airplane_id=airplane_id,
        )

class FlightDetailSerializer(serializers.ModelSerializer):
    airplane = AirplaneReadSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "airplane_id",
            "departure",
            "destination",
            "departure_time",
            "arrival_time",
            "airplane",
        )