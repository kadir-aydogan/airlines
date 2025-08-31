from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.api.flight.serializers import FlightCreateSerializer, FlightListSerializer, FlightsQuerySerializer, \
    FlightUpdateSerializer
from apps.core.api.pagination import DefaultPagination
from apps.core.api.reservation.serializers import ReservationsQuerySerializer, ReservationListSerializer
from apps.core.selectors.flight_selector import list_flights
from apps.core.selectors.reservation_selector import list_reservations
from apps.core.services.flight_services import create_flight, update_flight, soft_delete_flight


class FlightViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination

    def get_queryset(self):
        qp = FlightsQuerySerializer(data=self.request.query_params)
        qp.is_valid(raise_exception=True)
        return list_flights(**qp.validated_data)

    def get_serializer_class(self):
        return FlightCreateSerializer if self.action == "create" else FlightListSerializer

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

        ser = ReservationListSerializer(qs, many=True)

        return Response(ser.data)
