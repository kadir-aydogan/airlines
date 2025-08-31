from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.core.api.pagination import DefaultPagination
from apps.core.api.reservation.serializers import ReservationListSerializer, ReservationCreateSerializer, \
    ReservationsQuerySerializer, ReservationUpdateSerializer
from apps.core.models import Reservation
from apps.core.selectors.reservation_selector import list_reservations
from apps.core.services.reservation_services import make_reservation, update_reservation, soft_delete_reservation


class ReservationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination

    filter_backends = []

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        elif self.action == "create":
            return ReservationCreateSerializer
        elif self.action == "update" or self.action == "partial_update":
            return ReservationUpdateSerializer
        return None

    def get_queryset(self):
        base = Reservation.objects.select_related("flight").filter().order_by("id")

        if self.action == "list":
            qp = ReservationsQuerySerializer(data=self.request.query_params)
            qp.is_valid(raise_exception=True)
            return list_reservations(**qp.validated_data).select_related("flight")
        return base

    def perform_create(self, serializer: ReservationCreateSerializer):
        inp = serializer.to_input()
        reservation = make_reservation(inp)
        serializer.instance = reservation


    def perform_update(self, serializer: ReservationUpdateSerializer):
        obj = self.get_object()
        inp = serializer.to_input()
        update_reservation(obj, inp)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        soft_delete_reservation(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)





