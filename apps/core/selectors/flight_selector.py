from typing import Optional

from django.db.models import Q, QuerySet

from apps.core.models import Flight

def get_flight(
        *,
        flight_id: int,
        deleted: Optional[bool] = False) -> Optional[Flight]:

    return Flight.objects.select_related("airplane").get(id=flight_id, deleted=deleted)


def list_flights(
        *,
        airplane_id: Optional[int] = None,
        departure: Optional[str] = None,
        destination: Optional[str] = None,
        departure_time=None,
        departure_time_min=None,
        departure_time_max=None,
        arrival_time=None,
        arrival_time_min=None,
        arrival_time_max=None,
        search: Optional[str] = None,
        deleted: Optional[bool] = False,
) -> QuerySet[Flight]:

    qs = Flight.objects.all()

    if airplane_id is not None:
        qs = qs.filter(airplane_id=airplane_id)

    if departure:
        qs = qs.filter(departure=departure)

    if destination:
        qs = qs.filter(destination=destination)

    if departure_time:
        qs = qs.filter(departure_time=departure_time)
    else:
        if departure_time_min:
            qs = qs.filter(departure_time__gte=departure_time_min)

        if departure_time_max:
            qs = qs.filter(departure_time__lte=departure_time_max)

    if arrival_time:
        qs = qs.filter(arrival_time=arrival_time)
    else:
        if arrival_time_min:
            qs = qs.filter(arrival_time__gte=arrival_time_min)
        if arrival_time_max:
            qs = qs.filter(arrival_time__lte=arrival_time_max)

    if deleted:
        qs = qs.filter(deleted=False)

    if search:
        s = search.strip()
        qs = qs.filter(
            Q(flight_number__icontains=s) |
            Q(departure__icontains=s) |
            Q(destination__icontains=s)
        )

    qs = qs.order_by(
        "departure_time")

    return qs
