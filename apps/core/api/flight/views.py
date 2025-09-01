from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.drf import BaseResponseJSONRenderer, base_response_exception_handler
from apps.core.api.flight.serializers import FlightCreateSerializer, FlightReadSerializer, FlightsQuerySerializer, \
    FlightUpdateSerializer
from apps.core.api.pagination import DefaultPagination
from apps.core.api.reservation.serializers import ReservationsQuerySerializer, ReservationReadSerializer
from apps.core.models import Flight
from apps.core.selectors.flight_selector import list_flights
from apps.core.selectors.reservation_selector import list_reservations
from apps.core.services.flight_services import create_flight, update_flight, soft_delete_flight


class FlightViewSet(viewsets.ModelViewSet):
    renderer_classes = [BaseResponseJSONRenderer]
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination

    def get_queryset(self):
        base = Flight.objects.select_related("airplane").filter(deleted=False).order_by("id")

        if self.action == "list":
            qp = FlightsQuerySerializer(data=self.request.query_params)
            qp.is_valid(raise_exception=True)
            return list_flights(**qp.validated_data)

        return base

    def get_serializer_class(self):
        if self.action == "create":
            return FlightCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return FlightUpdateSerializer
        elif self.action == "retrieve":
            return FlightReadSerializer

        return FlightReadSerializer

    def perform_create(self, create_serializer: FlightCreateSerializer):
        inp = create_serializer.to_input()
        obj = create_flight(inp)
        create_serializer.instance = obj

    def perform_update(self, serializer: FlightUpdateSerializer):
        obj = self.get_object()
        inp = serializer.to_input()
        update_flight(obj, inp)

    def destroy(self, request, *args, **kwargs):
        flight = self.get_object()
        soft_delete_flight(flight)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="reservations")
    def reservations(self, request, pk=None):
        flight = self.get_object()

        qp = ReservationsQuerySerializer(data=request.query_params)
        qp.is_valid(raise_exception=True)

        params = {**qp.validated_data, "flight_id": flight.id}
        qs = list_reservations(**params)

        flight_data = self.get_serializer(flight).data

        ser = ReservationReadSerializer(qs, many=True)

        return Response({
            **flight_data,
            "reservations": ser.data,
        })

    def handle_exception(self, exc):
        print("Exception in API:", repr(exc))
        resp = base_response_exception_handler(exc, self.get_exception_handler_context())
        return resp or super().handle_exception(exc)
