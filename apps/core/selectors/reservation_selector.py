from typing import Optional

from django.db.models import QuerySet

from apps.core.models import Reservation


def list_reservations(
    *,
    reservation_code: Optional[str] = None,
    flight_id: Optional[int] = None,
    passenger_email: Optional[str] = None,
    passenger_name: Optional[str] = None,
    status: Optional[bool] = True,
    deleted: Optional[bool] = False,
    ordering: Optional[str] = None,
) -> QuerySet[Reservation]:

    qs = Reservation.objects.all()

    if reservation_code:
        qs = qs.filter(reservation_code=reservation_code)

    if flight_id is not None:
        qs = qs.filter(flight_id=flight_id)

    if passenger_email:
        qs = qs.filter(passenger_email=passenger_email)

    if passenger_name:
        qs = qs.filter(passenger_name=passenger_name)

    if status is not None:
        qs = qs.filter(status=status)

    if deleted is not None:
        qs = qs.filter(deleted=deleted)

    allowed = {"id", "-id", "created_at", "-created_at"}

    return qs.order_by(ordering if ordering in allowed else "id")