from dataclasses import dataclass, asdict
from datetime import timedelta

from django.db import transaction, connection
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.core.models import Flight, Reservation
from apps.core.selectors.flight_selector import list_flights, get_flight
from apps.core.services.flight_services import check_if_flight_is_passed
from apps.notifications.tasks import send_reservation_email_task

THRESHOLD = 60


@dataclass(frozen=True)
class MakeReservationInput:
    passenger_name: str
    passenger_email: str
    flight_id: int
    status: bool = True

@dataclass(frozen=True)
class UpdateReservationInput:
    passenger_name: str
    passenger_email: str
    flight_id: int
    status: bool = True


def make_reservation(inp: MakeReservationInput) -> Reservation:

    with transaction.atomic():

        flight = Flight.objects.select_related("airplane").get(pk=inp.flight_id, deleted=False)

        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [flight.id])

        active_reservation_count = Reservation.objects.select_for_update(of=("self",)).filter(flight=flight, status=True, deleted=False).count()

        if active_reservation_count >= flight.airplane.capacity:
            raise ValidationError("Flight capacity is full.")

        res = Reservation(
            flight=flight,
            passenger_name=inp.passenger_name,
            passenger_email=inp.passenger_email,
            status=inp.status,
        )

        res.full_clean()
        res.save()

        transaction.on_commit(lambda: send_reservation_email_task.delay(res.id))

        return res

def update_reservation(reservation: Reservation, inp: UpdateReservationInput) -> Reservation:
    changes = {k: v for k, v in asdict(inp).items() if v is not None}

    if not changes:
        return reservation
    for field, value in changes.items():
        setattr(reservation, field, value)

    with transaction.atomic():
        flight = Flight.objects.select_related("airplane").get(pk=reservation.flight_id, deleted=False)

        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [flight.id])

        active_reservation_count = Reservation.objects.select_for_update(of=("self",)).filter(flight=flight, status=True, deleted=False).exclude(id=reservation.id).count()

        if active_reservation_count >= flight.airplane.capacity:
            raise ValidationError("Flight capacity is full.")

        reservation.full_clean()

        reservation.save()

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



