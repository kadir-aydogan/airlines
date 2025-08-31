from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import status

from apps.core.api.airplanes.serializers import AirplaneCreateSerializer, AirplaneListSerializer, \
    AirplaneQuerySerializer, AirplaneUpdateSerializer, AirplaneDetailSerializer
from apps.core.api.flight.serializers import FlightsQuerySerializer, FlightListSerializer
from apps.core.api.pagination import DefaultPagination
from apps.core.models import Airplane
from apps.core.selectors import list_airplanes
from apps.core.selectors.flight_selector import list_flights
from apps.core.services import *
from apps.core.services.airplane_services import update_airplane, soft_delete_airplane


class AirplaneViewSet(viewsets.ModelViewSet):

    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    filter_backends = []

    def get_queryset(self):
        base = (
            Airplane.objects
            .only("id", "tail_number", "model", "capacity", "production_year", "status")
            .order_by("id")
        )

        if self.action == "list":
            qp = AirplaneQuerySerializer(data=self.request.query_params)
            qp.is_valid(raise_exception=True)
            return list_airplanes(**qp.validated_data)

        return base


    def get_serializer_class(self):
        if self.action == "create":
            return AirplaneCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return AirplaneUpdateSerializer
        elif self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneListSerializer


    def perform_create(self, create_serializer: AirplaneCreateSerializer):
        inp = create_serializer.to_input()
        airplane = create_airplane(inp)
        create_serializer.instance = airplane

    def perform_update(self, update_serializer: AirplaneUpdateSerializer):
        airplane = self.get_object()
        inp = update_serializer.to_input()
        airplane = update_airplane(airplane, inp)
        update_serializer.instance = airplane


    def destroy(self, request, *args, **kwargs):

        airplane = self.get_object()
        soft_delete_airplane(airplane)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="flights")
    def flights(self, request, pk=None):

        airplane = self.get_object()

        qp = FlightsQuerySerializer(data=request.query_params)
        qp.is_valid(raise_exception=True)

        flights_qs = list_flights(**qp.validated_data, airplane_id=airplane.id)

        airplane_data = self.get_serializer(airplane).data
        flights_data = FlightListSerializer(flights_qs, many=True).data

        return Response({
            **airplane_data,
            "flights": flights_data
        })


