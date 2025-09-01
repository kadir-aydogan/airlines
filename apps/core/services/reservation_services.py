from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import timedelta
from typing import Optional

from django.db import transaction, connection
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.models import Flight, Reservation
from apps.core.selectors.flight_selector import get_flight
from apps.core.services.flight_services import check_if_flight_is_passed, check_if_flight_is_started
from apps.notifications.dispatcher import publish_event

THRESHOLD = 60


@dataclass(frozen=True)
class MakeReservationInput:
    passenger_name: str
    passenger_email: str
    flight_id: int
    status: bool = True

@dataclass(frozen=True)
class UpdateReservationInput:
    passenger_name: Optional[str]
    passenger_email: Optional[str]
    status: bool = True

@contextmanager
def lock_flight_tx(flight_id: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [flight_id])
    yield


def ensure_flight_open_and_has_capacity(flight, *, exclude_reservation_id: int | None = None) -> None:
    # uçuş başladı mı?
    if check_if_flight_is_started(flight.id):
        raise ValidationError({"flight": f"Flight {flight.id} already passed."})

    # kapasite kontrolü + lock
    with lock_flight_tx(flight.id):
        qs = (Reservation.objects
              .select_for_update(of=("self",))
              .filter(flight=flight, status=True, deleted=False))
        if exclude_reservation_id:
            qs = qs.exclude(id=exclude_reservation_id)

        active_count = qs.count()
        if active_count >= flight.airplane.capacity:
            raise ValidationError({"flight": "Flight capacity is full."})


@transaction.atomic
def make_reservation(inp: MakeReservationInput) -> Reservation:

    flight = Flight.objects.select_related("airplane").get(pk=inp.flight_id, deleted=False)

    ensure_flight_open_and_has_capacity(flight)

    res = Reservation(
        flight=flight,
        passenger_name=inp.passenger_name,
        passenger_email=inp.passenger_email,
        status=inp.status,
    )

    res.full_clean()
    res.save()

    payload = {
        "passenger_email": res.passenger_email,
        "passenger_name": res.passenger_name,
        "flight_id": flight.id,
        "departure": flight.departure,
        "departure_time": flight.departure_time.isoformat(),
    }

    publish_event("reservation.booked", payload)

    return res

@transaction.atomic
def update_reservation(reservation: Reservation, inp: UpdateReservationInput) -> Reservation:
    changes = {k: v for k, v in asdict(inp).items() if v is not None}

    if not changes:
        return reservation
    for field, value in changes.items():
        setattr(reservation, field, value)

    reservation.full_clean()
    reservation.save(update_fields=changes.keys())

    # if target_status:
    #     payload = {
    #         "passenger_email": reservation.passenger_email,
    #         "passenger_name": reservation.passenger_name,
    #         "flight_id": flight.id,
    #         "departure": flight.departure,
    #         "departure_time": flight.departure_time.isoformat(),
    #     }
    #     publish_event("reservation.booked", payload)

    return reservation

def is_flight_soon(flight_id, threshold_minutes: int = THRESHOLD) -> bool:
    now = timezone.now()

    flight = get_flight(flight_id=flight_id)

    time_to_departure = flight.departure_time - now

    return timedelta(minutes=0) <= time_to_departure <= timedelta(minutes=threshold_minutes)


def soft_delete_reservation(reservation: Reservation):

    if reservation.deleted:
        return

    passed = check_if_flight_is_passed(reservation.flight_id)

    if not passed and is_flight_soon(flight_id=reservation.flight_id):
        raise ValidationError("There are only a few minutes to flight. You can not cancel your reservation after " + str(THRESHOLD) + " minutes remaining to flight.")

    reservation.deleted = True
    reservation.save()


